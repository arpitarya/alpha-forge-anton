"""LLMGateway — single entry point for all LLM completions."""

from __future__ import annotations

import asyncio
import logging

from alphaforge_llm.cost_guard import CostGuard, CostGuardError
from alphaforge_llm.handover import Handover
from alphaforge_llm.providers import REGISTRY
from alphaforge_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_llm.rate_limiter import RateLimiter
from alphaforge_llm.router import QueryRouter
from alphaforge_llm.types import Message, ProviderResponse, QueryType, ToolSchema

logger = logging.getLogger(__name__)


class LLMGateway:
    def __init__(self) -> None:
        self._registry = REGISTRY
        self._router = QueryRouter()
        self._rate = RateLimiter()
        self._guard = CostGuard()
        self._handover = Handover()

    async def complete(
        self,
        messages: list[Message],
        *,
        query_type: QueryType = QueryType.FACTOID,
        preferred_provider: str | None = None,
        tools: list[ToolSchema] | None = None,
        confirmed: bool = False,
    ) -> ProviderResponse:
        available = await self._available_providers()
        if preferred_provider and preferred_provider in available:
            provider_name = preferred_provider
        else:
            provider_name = self._router.pick(query_type, available)
        if not provider_name:
            raise RuntimeError("No providers available — check API keys")

        self._guard.check(provider_name, confirmed=confirmed)
        await self._rate.acquire(provider_name)

        adapter = self._registry[provider_name]
        prepared = self._handover.prepare(messages)

        try:
            result = await adapter.complete(prepared, tools=tools)
            assert isinstance(result, ProviderResponse)
            return result
        except CostGuardError:
            raise
        except Exception as exc:
            logger.warning("Provider %s failed (%s); trying fallback", provider_name, exc)
            return await self._fallback(
                query_type, available - {provider_name}, prepared, tools, confirmed,
            )

    async def _fallback(
        self,
        query_type: QueryType,
        remaining: set[str],
        messages: list[Message],
        tools: list[ToolSchema] | None,
        confirmed: bool,
    ) -> ProviderResponse:
        for name in self._router.chain_for(query_type):
            if name not in remaining:
                continue
            try:
                self._guard.check(name, confirmed=confirmed)
                await self._rate.acquire(name)
                result = await self._registry[name].complete(messages, tools=tools)
                assert isinstance(result, ProviderResponse)
                return result
            except Exception as exc:
                logger.warning("Fallback %s also failed: %s", name, exc)
        raise RuntimeError(f"All providers failed for {query_type}")

    async def health(self) -> dict[str, ProviderHealth]:
        tasks = {name: adapter.health() for name, adapter in self._registry.items()}
        results = await asyncio.gather(*tasks.values(), return_exceptions=False)
        return dict(zip(tasks.keys(), results, strict=True))

    async def _available_providers(self) -> set[str]:
        healths = await self.health()
        return {name for name, h in healths.items() if h.available}


def create_gateway() -> LLMGateway:
    return LLMGateway()
