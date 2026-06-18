"""Agentic tool loop — native function-calling on the trusted claude-sdk lane only.
Non-trusted/unconfirmed → ([], None) immediately. Mutating tools emit a confirm
card then break — awaiting async user approval. MAX_ROUNDS=5. Errors → error event.
"""
from __future__ import annotations

import json
import os
import time

from alphaforge_anton_llm.types import ProviderResponse

from app.modules.concierge import deep_search_service
from app.modules.concierge.tool_executor import build_confirm, execute_read
from app.modules.concierge.tool_registry import DEEP_SEARCH_TOOL, MUTATING_TOOLS, trusted_schemas

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
        results, has_confirm = [], False
        for tb in tool_blocks:
            t1 = time.perf_counter()
            if tb.name == DEEP_SEARCH_TOOL:
                evs, result_text, hc = await deep_search_service.dispatch(mode, dict(tb.input))
                events.extend(evs)
                has_confirm = has_confirm or hc
            elif tb.name in MUTATING_TOOLS:
                events.append({"confirm": build_confirm(tb.name, dict(tb.input))})
                result_text, has_confirm = "Awaiting user confirmation.", True
            else:
                try:
                    data = await execute_read(tb.name, dict(tb.input))
                    result_text = json.dumps(data, default=str)
                    events.append({"tool": {"name": tb.name, "detail": f"{len(result_text)} chars",
                                            "ms": int((time.perf_counter() - t1) * 1000)}})
                except Exception as exc:
                    result_text = f"error: {exc}"
                    events.append({"error": f"{tb.name}: {exc}"})
            results.append({"type": "tool_result", "tool_use_id": tb.id, "content": result_text})

        turns.append({"role": "user", "content": results})
        if has_confirm:
            return events, ProviderResponse(content=text or "Action proposed — please confirm.",
                                            provider="claude-sdk", model=model,
                                            prompt_tokens=resp.usage.input_tokens,
                                            completion_tokens=resp.usage.output_tokens)

    return events, ProviderResponse(content=text or "", provider="claude-sdk", model=model)
