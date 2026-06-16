"""Agent-initiated deep search — the confirm-gated glue over grounding_service.

Orff calls ``request_deep_search(reasons, queries)`` when it spots a fresh-data gap.
``confirm_card`` renders the ApprovalCard (no Parallel call — free until confirmed);
``run`` is the executor the card's apply endpoint (and Always mode) invokes: one
``grounding_service.run`` per query, each a tagged Cage receipt. Fail-open and
budget-capped throughout — over budget degrades to the free sources, never an error.
See docs/deep-search-ask.handoff.md.
"""

from __future__ import annotations

import time

from app.modules.concierge import grounding_service
from app.modules.concierge.tool_registry import DEEP_SEARCH_TOOL
from app.modules.signals.strategy_config import load_config

# Shown estimate per ask (Parallel Search ≈ ₹0.4/req); the live mtd/budget follow it.
_EST = "~₹0.5"


def confirm_card(reasons: str, queries: list[str]) -> dict:
    """ApprovalCard payload for request_deep_search. Pure save for the budget read —
    makes NO Parallel call. Over budget ⇒ no apply target, so it can't trigger a run."""
    mtd, budget, over = grounding_service.budget_status()
    if over:
        detail = f"Deep-search budget used (₹{mtd} of ₹{budget}) — will answer from free sources"
        apply = None
    else:
        detail = f"{_EST} · ₹{mtd} of ₹{budget} used this month"
        apply = {"path": "/api/v1/concierge/deep-search", "body": {"queries": list(queries)}}
    card = {
        "id": "deep-search",
        "action": "Deep web search",
        "summary": reasons,
        "steps": list(queries),
        "detail": detail,
    }
    if apply:
        card["apply"] = apply
    return card


async def run(queries: list[str]) -> str:
    """Run the confirmed queries through the shared executor; return grounded text.
    Fail-open: over budget or no results ⇒ a free-source instruction, never an error."""
    mtd, budget, over = grounding_service.budget_status()
    if over:
        return (f"Deep-search budget used (₹{mtd} of ₹{budget}) — "
                "answer from the free sources and say so.")
    allow_task = load_config().parallel.allow_task_api
    parts: list[str] = []
    for q in queries:
        if not q.strip():
            continue
        g = await grounding_service.run(q, kind=grounding_service.kind(q, allow_task))
        if g:
            parts.append(g.text)
    if not parts:
        return "No web results — answer from the free sources and say what couldn't be verified."
    return "\n\n".join(parts)


async def dispatch(mode: str, args: dict) -> tuple[list[dict], str, bool]:
    """Tool-loop handler for request_deep_search. Always = run cardless (loop continues);
    Auto = emit a confirm card and pause. Returns (events, tool_result_text, paused)."""
    queries = args.get("queries") or []
    if mode == "always":
        t = time.perf_counter()
        text = await run(queries)
        ms = int((time.perf_counter() - t) * 1000)
        ev = {"tool": {"name": DEEP_SEARCH_TOOL, "detail": "auto-confirmed", "ms": ms}}
        return [ev], text, False
    return ([{"confirm": confirm_card(args.get("reasons", ""), queries)}],
            "Awaiting user confirmation.", True)
