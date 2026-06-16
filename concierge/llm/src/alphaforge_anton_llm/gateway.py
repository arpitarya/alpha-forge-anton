"""LLMGateway — single entry point for all LLM completions."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator

from alphaforge_anton_llm import cage_meter
from alphaforge_anton_llm.cost_guard import CostGuard, CostGuardError
from alphaforge_anton_llm.handover import Handover
from alphaforge_anton_llm.providers import REGISTRY
from alphaforge_anton_llm.providers.base import ProviderHealth
from alphaforge_anton_llm.rate_limiter import RateLimiter
from alphaforge_anton_llm.router import QueryRouter
from alphaforge_anton_llm.types import Message, ProviderResponse, QueryType, ToolSchema

logger = logging.getLogger(__name__)


def _ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


class LLMGateway:
    def __init__(self) -> None:
        self._registry = REGISTRY
        self._router = QueryRouter()
        self._rate = RateLimiter()
        self._guard = CostGuard()
        self._handover = Handover()

    async def _select(
        self, qt: QueryType, preferred: str | None, confirmed: bool, model: str | None,
    ) -> tuple[str, set[str]]:
        available = await self._available_providers()
        pick = self._router.pick(qt, available)
        name = preferred if preferred and preferred in available else pick
        if not name:
            raise RuntimeError("No providers available — check API keys")
        # A pinned model only gates the guard when its provider is the one we picked.
        self._guard.check(name, model=model if name == preferred else None, confirmed=confirmed)
        await self._rate.acquire(name)
        return name, available

    async def complete(
        self, messages: list[Message], *,
        query_type: QueryType = QueryType.FACTOID,
        preferred_provider: str | None = None,
        model: str | None = None,
        tools: list[ToolSchema] | None = None,
        confirmed: bool = False,
    ) -> ProviderResponse:
        name, available = await self._select(query_type, preferred_provider, confirmed, model)
        # The pinned model id only applies to its own provider; a fallback uses its default.
        picked_model = model if name == preferred_provider else None
        prepared = self._handover.prepare(messages)
        t0 = time.monotonic()
        try:
            r = await self._registry[name].complete(prepared, tools=tools, model=picked_model)
            assert isinstance(r, ProviderResponse)
            cage_meter.record(r, query_type=query_type, latency_ms=_ms(t0))
            return r
        except CostGuardError:
            raise
        except Exception as exc:
            logger.warning("Provider %s failed (%s); falling back", name, exc)
            for nxt in self._router.chain_for(query_type):
                if nxt not in (available - {name}):
                    continue
                try:
                    self._guard.check(nxt, confirmed=confirmed)
                    await self._rate.acquire(nxt)
                    t1 = time.monotonic()
                    r = await self._registry[nxt].complete(prepared, tools=tools)
                    assert isinstance(r, ProviderResponse)
                    cage_meter.record(r, query_type=query_type, latency_ms=_ms(t1))
                    return r
                except Exception as e2:
                    logger.warning("Fallback %s also failed: %s", nxt, e2)
            raise RuntimeError(f"All providers failed for {query_type}") from exc

    async def stream(
        self, messages: list[Message], *,
        query_type: QueryType = QueryType.FACTOID,
        preferred_provider: str | None = None,
        model: str | None = None,
        confirmed: bool = False,
        reasoning: bool = False,
        effort: str | None = None,
    ) -> AsyncIterator[ProviderResponse]:
        """Stream ProviderResponse snapshots; one-shot when provider can't stream."""
        name, _ = await self._select(query_type, preferred_provider, confirmed, model)
        picked_model = model if name == preferred_provider else None
        adapter = self._registry[name]
        prepared = self._handover.prepare(messages)
        t0 = time.monotonic()
        # Phase 4: extended thinking only for reasoning intents on a capable adapter.
        kwargs: dict = {"model": picked_model}
        if reasoning and getattr(adapter, "supports_reasoning", False):
            extra = {"thinking": {"type": "adaptive", "display": "summarized"}}
            if effort:
                extra["output_config"] = {"effort": effort}
            kwargs["extra"] = extra
        if getattr(adapter, "supports_streaming", False) and hasattr(adapter, "astream"):
            last: ProviderResponse | None = None
            async for snapshot in adapter.astream(prepared, **kwargs):
                last = snapshot
                yield snapshot
            if last is not None:  # meter once from the final snapshot (cache split incl.)
                cage_meter.record(last, query_type=query_type, latency_ms=_ms(t0))
            return
        result = await adapter.complete(prepared, model=picked_model)
        assert isinstance(result, ProviderResponse)
        cage_meter.record(result, query_type=query_type, latency_ms=_ms(t0))
        yield result

    async def health(self) -> dict[str, ProviderHealth]:
        tasks = {name: adapter.health() for name, adapter in self._registry.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=False)
        return dict(zip(tasks.keys(), results, strict=True))

    async def _available_providers(self) -> set[str]:
        healths = await self.health()
        return {name for name, h in healths.items() if h.available}


def create_gateway() -> LLMGateway:
    return LLMGateway()
