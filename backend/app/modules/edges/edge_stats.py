"""Net-%-per-round-trip lists → `ResultStats`. Pure: no I/O, no clock.

The one place backtest statistics are computed, so gate 1 and gate 2 measure an edge
identically. Expectancy is the mean net %; turnover is round-trips annualised by the
holding period; max drawdown is the deepest dip on the cumulative net-% curve; Calmar
annualises the mean per-trade return by turnover and divides by max drawdown.
"""

from __future__ import annotations

from app.modules.edges.edge_schema import ResultStats

_TRADING_DAYS = 252.0
_DD_EPSILON = 0.5  # min drawdown denominator (%), so a drawdown-free run isn't Calmar 0


def _max_drawdown_pct(curve: list[float]) -> float:
    """Deepest peak-to-trough on a cumulative-% curve, as % of the peak (≥ 0)."""
    peak = dd = 0.0
    for equity in curve:
        peak = max(peak, equity)
        drop = peak - equity
        dd = max(dd, drop)
    return round(dd, 4)


def build_stats(nets: list[float], hold_days: int) -> ResultStats:
    if not nets:
        return ResultStats()
    n = len(nets)
    wins = sum(1 for x in nets if x > 0)
    curve, running = [], 0.0
    for x in nets:
        running += x
        curve.append(running)
    max_dd = _max_drawdown_pct(curve)
    expectancy = sum(nets) / n
    turnover = _TRADING_DAYS / max(1, hold_days)  # round-trips per year at this cadence
    annual_return = expectancy * turnover  # mean per-trade % x trips/yr
    # Calmar = annual return / max drawdown. A drawdown-free run is excellent, not a
    # divide-by-zero: floor the denominator at a small epsilon so a flawless winner
    # scores a large positive Calmar (and a no-DD loser a large negative), never 0.
    calmar = annual_return / max(max_dd, _DD_EPSILON)
    return ResultStats(
        trades=n,
        expectancy_pct=round(expectancy, 4),
        hit_rate=round(wins / n, 4),
        turnover=round(turnover, 2),
        max_dd_pct=max_dd,
        calmar=round(calmar, 4),
    )
