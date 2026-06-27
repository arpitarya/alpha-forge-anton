"""Build-time liquidity superset, turnover alignment, and per-rebalance Gate-0 for the real panel.

`liquid_superset` is the union of the weekly point-in-time top-N-by-trailing-median-turnover sets
across the whole range — every name that was ever liquid stays in (delisted names included), so the
committed panel is survivorship-safe yet bounded (far smaller than "every symbol ever traded").
`align_turnover` writes 0 on non-trading days (never forward-filled, unlike closes) — a pre-listing
or post-delisting name has zero turnover at those bars. `gate0_per_week` then asserts — reusing the
funnel's own `liquid_as_of` — that the eligible set at each rebalance ⊆ that day's traders: no
look-ahead, by the exact rule the backtest will apply.
"""

from __future__ import annotations

from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_universe import active, liquid_as_of
from app.modules.marketdata.bhavcopy_schema import BhavRow
from app.modules.marketdata.gate0_integrity import Gate0Error
from app.modules.marketdata.panel_utils import BarsByDay, median_turnover_rank


def liquid_superset(
    bars: BarsByDay, dates: list[str], top_n: int = 250, window: int = 60, step: int = 5
) -> list[str]:
    """Union of the weekly point-in-time top-N liquid sets over `dates` (minus excluded symbols)."""
    members: set[str] = set()
    for i in range(0, len(dates), step):
        members.update(median_turnover_rank(bars, dates[i], top_n, window))
    return sorted(members - active().symbols)


def align_turnover(bars: BarsByDay, dates: list[str], symbols: list[str]) -> dict[str, list[float]]:
    """Dense ₹ turnover per symbol; 0 on non-trading days (never carried forward, unlike closes)."""
    out: dict[str, list[float]] = {}
    for sym in sorted(symbols):
        series: list[float] = []
        for d in dates:
            bar = bars.get(d, {}).get(sym)
            series.append(bar.turnover if bar is not None else 0.0)
        out[sym] = series
    return out


def gate0_per_week(panel: dict, rows: list[BhavRow], step: int = 5) -> None:
    """Reject look-ahead: each rebalance's eligible set ⊆ that day's traders (the funnel's rule)."""
    p = Panel(
        dates=panel["dates"],
        closes=panel["closes"],
        nifty=panel["nifty"],
        turnover=panel["turnover"],
    )
    for t in range(0, len(p.dates), step):
        traders = {r.symbol for r in rows if r.date == p.dates[t]}
        leak = sorted(set(liquid_as_of(p, t)) - traders)
        if leak:
            raise Gate0Error(f"look-ahead at {p.dates[t]}: {leak}")
