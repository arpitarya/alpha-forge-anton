"""Claude SDK adapter — paid, gated by CostGuard + user confirmation."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.providers._claude_stream import claude_stream
from alphaforge_anton_llm.providers._claude_system import system_blocks
from alphaforge_anton_llm.providers._vision import parse_data_url
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolCall, ToolSchema

logger = logging.getLogger(__name__)


def _blocks(m: Message) -> str | list[dict]:
    """Plain text normally; content blocks when the turn carries images."""
    if not m.images:
        return m.content
    blocks: list[dict] = [
        {"type": "image", "source": {"type": "base64", "media_type": mime, "data": data}}
        for img in m.images if (parsed := parse_data_url(img)) for mime, data in [parsed]
    ]
    blocks.append({"type": "text", "text": m.content})
    return blocks


def _parse_blocks(content_blocks) -> str:
    """Concat text blocks; skip tool_use/thinking (Phase 2/4)."""
    return "".join(b.text for b in content_blocks if b.type == "text")


class ClaudeSdkAdapter(ProviderAdapter):
    name = "claude-sdk"
    env_key = "ANTHROPIC_API_KEY"
    supports_tool_calling = True
    supports_streaming = True
    supports_reasoning = True

    def __init__(self) -> None:
        self._last_error: str | None = None

    def _build_kwargs(self, messages: list[Message], model: str | None,
                      extra: dict | None = None) -> tuple:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Install anthropic: pip install anthropic") from exc
        if not (api_key := os.getenv("ANTHROPIC_API_KEY", "")):
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        model = model or self.default_model()
        client = anthropic.AsyncAnthropic(api_key=api_key)
        system = system_blocks(messages)
        turns = [{"role": m.role, "content": _blocks(m)} for m in messages if m.role != "system"]
        kw: dict = {"model": model, "max_tokens": pricing.max_tokens(self.name, model), "messages": turns}
        if system:
            kw["system"] = system
        if extra:  # Phase 4: thinking={adaptive…} / output_config={effort} for reasoning intents
            kw.update(extra)
        return client, model, kw

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
        model: str | None = None,
    ) -> ProviderResponse:
        client, model, kw = self._build_kwargs(messages, model)
        if tools:
            kw["tools"] = [{"name": t.name, "description": t.description, "input_schema": t.parameters} for t in tools]
        try:
            response = await client.messages.create(**kw)
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Claude SDK error: %s", exc)
            raise
        u = response.usage
        tc = [ToolCall(call_id=b.id, name=b.name, args=dict(b.input)) for b in response.content if b.type == "tool_use"]
        return ProviderResponse(
            content=_parse_blocks(response.content), provider=self.name, model=model,
            prompt_tokens=u.input_tokens, completion_tokens=u.output_tokens,
            cache_read_input_tokens=getattr(u, "cache_read_input_tokens", 0) or 0,
            cache_creation_input_tokens=getattr(u, "cache_creation_input_tokens", 0) or 0,
            tool_calls=tc,
        )

    async def astream(
        self, messages: list[Message], *, model: str | None = None,
        tools: list[ToolSchema] | None = None, extra: dict | None = None,
    ) -> AsyncIterator[ProviderResponse]:
        client, model, kw = self._build_kwargs(messages, model, extra)
        async for snap in claude_stream(client=client, model=model, provider_name=self.name, kw=kw):
            yield snap

    async def health(self) -> ProviderHealth:
        if not os.getenv("ANTHROPIC_API_KEY"):
            return self._err("ANTHROPIC_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
