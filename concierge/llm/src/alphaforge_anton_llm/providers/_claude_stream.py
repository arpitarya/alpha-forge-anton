"""Anthropic native streaming — yields cumulative ProviderResponse snapshots.

Mirrors _openai_stream.py: text_delta events grow `content`; message_start /
message_delta carry the token counts. thinking_delta is surfaced as a `<think>`
prefix (Phase 4); tool_use is handled by the concierge tool_layer (Phase 2).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from alphaforge_anton_llm.types import ProviderResponse


async def claude_stream(
    *, client, model: str, provider_name: str, kw: dict,
) -> AsyncIterator[ProviderResponse]:
    """Stream from `client.messages.stream(**kw)`; yield a ProviderResponse per chunk.

    Adaptive-thinking deltas are surfaced as a `<think>…</think>` prefix on content, so
    the existing `split_thinking` → `{thinking}` SSE path renders them (Phase 4)."""
    text, think, in_tok, out_tok, cr, cc = "", "", 0, 0, 0, 0

    def snap() -> ProviderResponse:
        content = f"<think>{think}</think>{text}" if think else text
        return ProviderResponse(
            content=content, provider=provider_name, model=model,
            prompt_tokens=in_tok, completion_tokens=out_tok,
            cache_read_input_tokens=cr, cache_creation_input_tokens=cc,
        )

    async with client.messages.stream(**kw) as stream:
        async for event in stream:
            t = event.type
            if t == "message_start":
                u = event.message.usage
                in_tok = u.input_tokens
                cr = getattr(u, "cache_read_input_tokens", 0) or 0
                cc = getattr(u, "cache_creation_input_tokens", 0) or 0
            elif t == "content_block_delta":
                d = event.delta
                if d.type == "text_delta":
                    text += d.text
                    yield snap()
                elif d.type == "thinking_delta":
                    think += d.thinking
                    yield snap()
            elif t == "message_delta":
                out_tok = event.usage.output_tokens
    yield snap()
