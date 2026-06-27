"""Pure helpers for assembling the dense liquidity panel — no I/O, no clock.

`median_turnover_rank` pins the universe **point-in-time as of `start`** (turnover over the
60 sessions ending at `start`, never any future day). `align_closes` densifies each symbol's
closes over the date axis, carrying the last real close across gaps and after a delist — so a
name that drops out mid-window is **kept** (survivorship-safe), not silently removed.
"""

from __future__ import annotations

import statistics

from app.modules.marketdata.bhavcopy_schema import BhavRow

BarsByDay = dict[str, dict[str, BhavRow]]  # ISO date → symbol → bar


def median_turnover_rank(bars: BarsByDay, start: str, top_n: int, window: int = 60) -> list[str]:
    """Top-N symbols by median ₹ turnover over the `window` sessions ending at `start`."""
    days = sorted(d for d in bars if d <= start)[-window:]
    turn: dict[str, list[float]] = {}
    for d in days:
        for sym, bar in bars[d].items():
            turn.setdefault(sym, []).append(bar.turnover)
    med = {s: statistics.median(v) for s, v in turn.items() if v}
    return sorted(med, key=lambda s: (-med[s], s))[:top_n]


def align_closes(bars: BarsByDay, dates: list[str], symbols: list[str]) -> dict[str, list[float]]:
    """Dense closes per symbol over `dates`; carry the last real close across gaps / delist."""
    out: dict[str, list[float]] = {}
    for sym in sorted(symbols):
        series: list[float] = []
        last = 0.0
        for d in dates:
            bar = bars.get(d, {}).get(sym)
            if bar is not None and bar.close:
                last = bar.close
            series.append(last)
        out[sym] = series
    return out
