"""Groq adapter — free tier, very fast Llama-3.3 and Gemma2."""

from __future__ import annotations

import logging
import os
from typing import AsyncIterator

from alphaforge_anton_llm.providers._openai_compat import openai_complete
from alphaforge_anton_llm.providers._openai_stream import openai_stream
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)

_BASE = "https://api.groq.com/openai/v1"
_MODEL = "llama-3.3-70b-versatile"


class GroqAdapter(ProviderAdapter):
    name = "groq"
    env_key = "GROQ_API_KEY"
    supports_tool_calling = True
    supports_streaming = True

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
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        try:
            result = await openai_complete(
                base_url=_BASE, api_key=api_key, model=_MODEL,
                provider_name=self.name, messages=messages, tools=tools,
            )
            self._last_error = None
            return result
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Groq error: %s", exc)
            raise

    async def astream(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
    ) -> AsyncIterator[ProviderResponse]:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        async for r in openai_stream(
            base_url=_BASE, api_key=api_key, model=_MODEL,
            provider_name=self.name, messages=messages,
        ):
            yield r

    async def health(self) -> ProviderHealth:
        if not os.getenv("GROQ_API_KEY"):
            return self._err("GROQ_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
