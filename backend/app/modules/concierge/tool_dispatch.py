"""One round of the agentic tool loop — run each tool_use block, collect tool_results.

Split out of `tool_layer` so that file stays within the line budget. Mutating tools
and the deep-search Auto card go through a once-only confirm guard: a confirm-card id
that repeats within a single turn collapses (the model is told it's already pending and
answers) instead of re-emitting — defense-in-depth against a confirm→apply re-arm spin.
See docs/orff-tool-calling.handoff.md and concierge/README.md §9.
"""
from __future__ import annotations

import json
import time

from app.modules.concierge import deep_search_service
from app.modules.concierge.tool_executor import build_confirm, execute_read
from app.modules.concierge.tool_registry import DEEP_SEARCH_TOOL, MUTATING_TOOLS


def _emit_confirm(card: dict, events: list, seen: set[str]) -> tuple[str, bool]:
    """Emit a confirm card once; a repeat id collapses. Returns (tool_result, emitted)."""
    cid = card.get("id", "")
    if cid in seen:
        return (f"Action '{cid}' is already pending the user's confirmation — "
                "do not re-propose it; answer the user instead.", False)
    seen.add(cid)
    events.append({"confirm": card})
    return "Awaiting user confirmation.", True


async def run_blocks(
    tool_blocks, mode: str, events: list, seen: set[str]
) -> tuple[list[dict], bool]:
    """Execute one round's tool_use blocks → (tool_results, has_confirm). Appends UI
    events (tool/confirm/error) to `events`; `seen` carries confirm ids across rounds."""
    results, has_confirm = [], False
    for tb in tool_blocks:
        t1 = time.perf_counter()
        if tb.name == DEEP_SEARCH_TOOL:
            evs, result_text, _ = await deep_search_service.dispatch(mode, dict(tb.input))
            for ev in evs:  # route a confirm card through the once-only guard
                if "confirm" in ev:
                    result_text, emitted = _emit_confirm(ev["confirm"], events, seen)
                    has_confirm = has_confirm or emitted
                else:
                    events.append(ev)
        elif tb.name in MUTATING_TOOLS:
            card = build_confirm(tb.name, dict(tb.input))
            result_text, emitted = _emit_confirm(card, events, seen)
            has_confirm = has_confirm or emitted
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
    return results, has_confirm
