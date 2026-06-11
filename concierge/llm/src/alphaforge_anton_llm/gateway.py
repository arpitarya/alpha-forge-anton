"""LLMGateway — single entry point for all LLM completions."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from alphaforge_anton_llm.cost_guard import CostGuard, CostGuardError
from alphaforge_anton_llm.handover import Handover
from alphaforge_anton_llm.providers import REGISTRY
from alphaforge_anton_llm.providers.base import ProviderHealth
from alphaforge_anton_llm.rate_limiter import RateLimiter
from alphaforge_anton_llm.router import QueryRouter
from alphaforge_anton_llm.types import Message, ProviderResponse, QueryType, ToolSchema

logger = logging.getLogger(__name__)


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
        try:
            r = await self._registry[name].complete(prepared, tools=tools, model=picked_model)
            assert isinstance(r, ProviderResponse)
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
                    r = await self._registry[nxt].complete(prepared, tools=tools)
                    assert isinstance(r, ProviderResponse)
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
    ) -> AsyncIterator[ProviderResponse]:
        """Stream ProviderResponse snapshots; one-shot when provider can't stream."""
        name, _ = await self._select(query_type, preferred_provider, confirmed, model)
        picked_model = model if name == preferred_provider else None
        adapter = self._registry[name]
        prepared = self._handover.prepare(messages)
        if getattr(adapter, "supports_streaming", False) and hasattr(adapter, "astream"):
            async for snapshot in adapter.astream(prepared, model=picked_model):
                yield snapshot
            return
        result = await adapter.complete(prepared, model=picked_model)
        assert isinstance(result, ProviderResponse)
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
