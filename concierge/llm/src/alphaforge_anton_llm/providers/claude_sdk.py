"""Claude SDK adapter — paid, gated by CostGuard + user confirmation."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.providers._vision import parse_data_url
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)


def _blocks(m: Message) -> str | list[dict]:
    """Plain text normally; content blocks when the turn carries images."""
    if not m.images:
        return m.content
    blocks: list[dict] = [
        {"type": "image",
         "source": {"type": "base64", "media_type": mime, "data": data}}
        for img in m.images if (parsed := parse_data_url(img)) for mime, data in [parsed]
    ]
    blocks.append({"type": "text", "text": m.content})
    return blocks


class ClaudeSdkAdapter(ProviderAdapter):
    name = "claude-sdk"
    env_key = "ANTHROPIC_API_KEY"
    supports_tool_calling = True
    supports_streaming = False

    def __init__(self) -> None:
        self._last_error: str | None = None

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
        model: str | None = None,
    ) -> ProviderResponse | AsyncIterator[str]:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Install anthropic: pip install anthropic") from exc

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        model = model or self.default_model()
        client = anthropic.AsyncAnthropic(api_key=api_key)
        # Join ALL system messages — the gateway appends grounding and the private
        # holdings disclosure as extra system turns; dropping them leaks intent.
        system_parts = [m.content for m in messages if m.role == "system"]
        system = "\n\n".join(system_parts) if system_parts else None
        turns = [{"role": m.role, "content": _blocks(m)} for m in messages if m.role != "system"]
        max_tokens = pricing.max_tokens(self.name, model)
        kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": turns}
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
            content=text, provider=self.name, model=model,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
        )

    async def health(self) -> ProviderHealth:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return self._err("ANTHROPIC_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
