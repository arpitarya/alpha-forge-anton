"""Typed NSE bhavcopy shapes — one daily OHLCV bar and a point-in-time universe.

`BhavRow` is one symbol's bar on one trading session (dates are ISO, so the same input
serialises byte-identically). `UniverseSnapshot` is the set of symbols actually trading on
the session at `as_of` — the only honest universe a point-in-time backtest may read.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BhavRow(BaseModel):
    """One symbol's daily OHLCV bar from an NSE bhavcopy."""

    date: str  # ISO trading date (YYYY-MM-DD)
    symbol: str
    series: str = "EQ"
    isin: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    turnover: float = 0.0  # traded value in ₹ — feeds the 60-day-median liquidity universe


class UniverseSnapshot(BaseModel):
    """Symbols trading on the session at `as_of` — survivorship- and look-ahead-safe."""

    as_of: str  # ISO date the universe is pinned to
    symbols: list[str] = Field(default_factory=list)
