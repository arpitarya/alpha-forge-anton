"""Signals/plan context injected into Orff for signals-intent turns (handoff §7).

Best-effort + timeboxed: assembles the active strategy config, the latest saved
plan + diff vs today, top screener candidates, and matched news as one system
block Orff narrates (the `strategy-knob-tradeoffs` Fux rule already arrives via
grounding). Gated to signals-intent prompts so normal chat stays fast/free; any
piece that errors or times out is skipped — never blocks the stream. The fresh
ActionPlan itself is delivered by `/signals/review` (its card), not recomputed here.
"""

from __future__ import annotations

import asyncio
import logging

from alphaforge_anton_llm.types import Message

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.signals import plan_diff, plan_store
from app.modules.signals.screen_service import build_screen
from app.modules.signals.strategy_config import load_config

logger = logging.getLogger(__name__)

_INTENT = ("review", "plan", "screen", "buy", "sell", "trim", "strateg", "signal", "candidate")
_PREAMBLE = (
    "Signals-engine context (deterministic — narrate these, don't recompute the numbers; "
    "cite strategy-knob-tradeoffs when discussing a change):\n\n"
)
_BUDGET_S = 8.0


def wants(text: str) -> bool:
    t = (text or "").lower()
    return any(w in t for w in _INTENT)


async def _news(symbols: list[str]) -> str | None:
    from app.modules.news.news_service import get_aggregator

    items = await get_aggregator().search("Indian equity news", symbols=symbols, limit=5)
    heads = [i.headline for i in items[:5] if getattr(i, "headline", None)]
    return ("Matched news: " + " · ".join(heads)) if heads else None


async def _block() -> str:
    cfg = load_config()
    parts = [
        f"Active strategy: universe={cfg.universe.mode}, trim={cfg.trim_rule.mode}, "
        f"hard_stop={cfg.stops.hard_pct:.0f}%, trim_at={cfg.trim_rule.trim_at_pct:.0f}%, "
        f"max_weight={cfg.trim_rule.max_weight_pct:.0f}%."
    ]
    holdings = HoldingsAggregator().all_holdings()
    if last := await plan_store.latest():
        d = plan_diff.diff(holdings, last)
        verds = "; ".join(f"{v.action.value.upper()} {v.symbol}" for v in last.verdicts[:12])
        parts.append(f"Last saved plan {last.plan_id}: {verds or '—'}")
        parts.append(
            f"Changed since: exited={d.exited or '—'}, new={d.new_positions or '—'}, "
            f"stops_fired={d.stops_fired or '—'}, unacted={d.unacted or '—'}"
        )
    else:
        parts.append("No saved plan yet — fresh review.")
    syms = [h.symbol for h in holdings[:8]]
    try:
        screen = await asyncio.wait_for(build_screen(limit=5), timeout=4.0)
        if screen.candidates:
            parts.append(
                "Top buy-candidates: "
                + ", ".join(f"{c.symbol}({c.score:.2f})" for c in screen.candidates)
            )
    except Exception as e:
        logger.debug("screen context skipped: %s", e)
    try:
        if news := await asyncio.wait_for(_news(syms), timeout=4.0):
            parts.append(news)
    except Exception as e:
        logger.debug("news context skipped: %s", e)
    return _PREAMBLE + "\n".join(parts)


async def inject(req, msgs: list[Message], trace: list[dict]) -> None:
    """Append the signals context block + a trace step for signals-intent turns."""
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    if not wants(last_user):
        return
    try:
        block = await asyncio.wait_for(_block(), timeout=_BUDGET_S)
    except Exception as e:
        logger.debug("signals context skipped: %s", e)
        return
    msgs.append(Message(role="system", content=block))
    trace.append(
        {
            "name": "signals.context",
            "detail": "strategy · last plan · diff · screen · news",
            "ms": 0,
        }
    )
