"""Agentic tool loop — native function-calling on the trusted claude-sdk lane only.
Non-trusted/unconfirmed → ([], None) immediately. Mutating tools emit a confirm
card then break — awaiting async user approval. MAX_ROUNDS=5. Errors → error event.
"""
from __future__ import annotations

import os

from alphaforge_anton_llm.types import ProviderResponse

from app.modules.concierge.tool_dispatch import run_blocks
from app.modules.concierge.tool_registry import trusted_schemas

_MAX_ROUNDS = 5


def _as_anthropic(schemas) -> list[dict]:
    return [{"name": s.name, "description": s.description, "input_schema": s.parameters}
            for s in schemas]


def _block_dict(b) -> dict:
    if b.type == "tool_use":
        return {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
    return {"type": "text", "text": getattr(b, "text", "")}


async def run(assembled, _gateway) -> tuple[list[dict], ProviderResponse | None]:
    """Tool pre-pass for trusted confirmed turns. Returns (events, final_response)."""
    if assembled.preferred != "claude-sdk" or not assembled.confirmed:
        return [], None
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return [{"error": "ANTHROPIC_API_KEY not set — tool loop unavailable"}], None
    try:
        import anthropic
    except ImportError:
        return [{"error": "anthropic package not installed"}], None

    client = anthropic.AsyncAnthropic(api_key=api_key)
    model = assembled.model or "claude-sonnet-4-6"
    system = ("\n\n".join(m.content for m in assembled.msgs if m.role == "system") or None)
    turns = [{"role": m.role, "content": m.content}
             for m in assembled.msgs if m.role != "system"]
    mode = assembled.deep_search_mode
    tools = _as_anthropic(trusted_schemas(offer_deep_search=mode != "never"))
    events: list = []
    seen_confirm: set[str] = set()  # confirm-card ids already emitted this call (re-arm guard)

    for _ in range(_MAX_ROUNDS):
        try:
            kw: dict = {"model": model, "max_tokens": 8192, "messages": turns, "tools": tools}
            if system:
                kw["system"] = system
            resp = await client.messages.create(**kw)
        except Exception as exc:
            events.append({"error": f"tool loop: {exc}"})
            return events, None

        text = "".join(getattr(b, "text", "") for b in resp.content)
        tool_blocks = [b for b in resp.content if b.type == "tool_use"]
        if not tool_blocks:
            return events, ProviderResponse(content=text, provider="claude-sdk", model=model,
                                            prompt_tokens=resp.usage.input_tokens,
                                            completion_tokens=resp.usage.output_tokens)

        turns.append({"role": "assistant", "content": [_block_dict(b) for b in resp.content]})
        results, has_confirm = await run_blocks(tool_blocks, mode, events, seen_confirm)
        turns.append({"role": "user", "content": results})
        if has_confirm:
            return events, ProviderResponse(content=text or "Action proposed — please confirm.",
                                            provider="claude-sdk", model=model,
                                            prompt_tokens=resp.usage.input_tokens,
                                            completion_tokens=resp.usage.output_tokens)

    return events, ProviderResponse(content=text or "", provider="claude-sdk", model=model)
