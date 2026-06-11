"""ProviderAdapter ABC — the contract every provider must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema


class ProviderHealth(BaseModel):
    available: bool
    model: str = ""
    quota_remaining: int | None = None
    last_error: str | None = None


class ProviderAdapter(ABC):
    name: str
    env_key: str
    supports_tool_calling: bool = True
    supports_streaming: bool = True

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
        model: str | None = None,
    ) -> ProviderResponse | AsyncIterator[str]: ...

    @abstractmethod
    async def health(self) -> ProviderHealth: ...

    @classmethod
    def default_model(cls) -> str:
        """The provider's default model id — the first entry in `providers.json`."""
        return registry.default_model(cls.name)

    def _ok(self) -> ProviderHealth:
        return ProviderHealth(available=True, model=self.default_model())

    def _err(self, msg: str) -> ProviderHealth:
        return ProviderHealth(available=False, model=self.default_model(), last_error=msg)
