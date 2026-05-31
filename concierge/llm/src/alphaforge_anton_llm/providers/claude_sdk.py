"""Claude SDK adapter — paid, gated by CostGuard + user confirmation."""

from __future__ import annotations

import logging
import os
from typing import AsyncIterator

from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-6"


class ClaudeSdkAdapter(ProviderAdapter):
    name = "claude-sdk"
    env_key = "ANTHROPIC_API_KEY"
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
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Install anthropic: pip install anthropic") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        client = anthropic.AsyncAnthropic(api_key=api_key)
        system = next((m.content for m in messages if m.role == "system"), None)
        turns = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        kwargs: dict = {"model": _MODEL, "max_tokens": 4096, "messages": turns}
        if system:
            kwargs["system"] = system
        try:
            response = await client.messages.create(**kwargs)
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Claude SDK error: %s", exc)
            raise

        text = response.content[0].text if response.content else ""
        return ProviderResponse(
            content=text, provider=self.name, model=_MODEL,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )

    async def health(self) -> ProviderHealth:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return self._err("ANTHROPIC_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
