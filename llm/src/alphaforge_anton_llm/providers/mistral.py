"""Mistral adapter — free tier, strong structured output / tool calling."""

from __future__ import annotations

import logging
import os
from typing import AsyncIterator

from alphaforge_anton_llm.providers._openai_compat import openai_complete
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)

_BASE = "https://api.mistral.ai/v1"
_MODEL = "mistral-small-latest"


class MistralAdapter(ProviderAdapter):
    name = "mistral"
    env_key = "MISTRAL_API_KEY"
    supports_tool_calling = True
    supports_streaming = False

    def __init__(self) -> None:
        self._last_error: str | None = None

    @classmethod
    def default_model(cls) -> str:
        return _MODEL

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
    ) -> ProviderResponse | AsyncIterator[str]:
        api_key = os.getenv("MISTRAL_API_KEY", "")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY not set")
        try:
            result = await openai_complete(
                base_url=_BASE, api_key=api_key, model=_MODEL,
                provider_name=self.name, messages=messages, tools=tools,
            )
            self._last_error = None
            return result
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Mistral error: %s", exc)
            raise

    async def health(self) -> ProviderHealth:
        if not os.getenv("MISTRAL_API_KEY"):
            return self._err("MISTRAL_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
