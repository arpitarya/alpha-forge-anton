"""Holdings disclosure renderers — percentage fallbacks + full rows for the trusted lane.

Pure rendering, no policy: `holdings_private.detailed_context()` is the chokepoint that
decides WHO may see `holdings_table()`. Everything here reads the HoldingsAggregator
roll-up (INR-normalised) and never fetches.
"""

from __future__ import annotations

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.fx import to_inr

NO_LIVE_DATA = (
    "Holdings context: no live broker data is cached right now, so allocation "
    "percentages are unavailable. Tell the user that plainly. Do NOT invent figures "
    "and do NOT show a sample/demo/illustrative holdings table — fabricated rows in "
    "a finance terminal read as real data. Instead, point the user to the broker "
    "sources panel to sync a broker (the CDP Chrome tab must be logged in) or to "
    "upload a holdings CSV, then continue the conversation."
)


def no_plan_context(plan_id: str) -> str:
    """Actuals-only, percentages-only fallback when the elgar store has no plan doc."""
    slices = HoldingsAggregator().allocation()
    if not slices:
        return NO_LIVE_DATA
    head = (
        f"Holdings context: no '{plan_id}' plan doc exists in the elgar store, so target "
        "percentages and drift are unavailable — do NOT invent targets, do NOT recommend "
        "rebalancing trades, and do NOT show a sample/demo/illustrative holdings table — "
        "fabricated rows in a finance terminal read as real data. Answer ONLY from the "
        "actual allocation below, PERCENTAGES ONLY (no amounts, no symbols):"
    )
    lines = [f"- {s.asset_class.value}: {s.pct:.0f}% of current portfolio" for s in slices]
    tail = (
        "Mention that committing a plan (`elgar save plan/<id>`) unlocks drift and "
        "rebalancing advice."
    )
    return head + "\n" + "\n".join(lines) + "\n" + tail


def _inr(v: float) -> str:
    return f"₹{v:,.0f}"


def holdings_table(max_rows: int = 60) -> str:
    """Every cached holding as one line, biggest first, plus the portfolio totals.

    Native-currency avg/ltp (tagged when non-INR); values and totals INR-normalised.
    Returns "" when no broker cache is populated — callers fall back to NO_LIVE_DATA.
    """
    agg = HoldingsAggregator()
    held = sorted(agg.all_holdings(), key=lambda h: -to_inr(h.current_value, h.currency))
    if not held:
        return ""
    lines = []
    for h in held[:max_rows]:
        cur = f" [{h.currency}]" if h.currency and h.currency != "INR" else ""
        lines.append(
            f"- [{h.source}] {h.symbol} · {h.asset_class.value}{cur}: qty {h.quantity:g} "
            f"@ avg {h.avg_price:,.2f}, ltp {h.last_price:,.2f} → "
            f"now {_inr(to_inr(h.current_value, h.currency))}, "
            f"P&L {h.pnl_pct:+.1f}%, day {h.day_change_pct:+.1f}%"
        )
    t = agg.totals()
    totals = (
        f"Totals: invested {_inr(t['invested'])}, current {_inr(t['current_value'])}, "
        f"P&L {_inr(t['pnl'])} ({t['pnl_pct']:+.1f}%), "
        f"day P&L {_inr(t['day_pnl'])} ({t['day_pnl_pct']:+.2f}%), {t['count']} holdings"
    )
    return "\n".join(lines) + "\n" + totals


__all__ = ["NO_LIVE_DATA", "holdings_table", "no_plan_context"]
