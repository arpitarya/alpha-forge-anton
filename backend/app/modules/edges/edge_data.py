"""The single data-source seam for the edge engine — free NSE daily to start.

Everything else in the module depends on `BarsProvider`, never on a concrete feed,
so an intraday or paid source swaps in here later without touching the gates. The
default `NSEDailyBars` reuses `signals.backtest_data.load_series` (free NSE daily via
yfinance, disk-cached, fail-open). A `Bars` is dated OHLC — dates carry the holding
period and STCG short/long classification downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.modules.signals.backtest_data import load_series


@dataclass(frozen=True)
class Bars:
    dates: list[str]  # ISO trading dates, aligned 1:1 with closes
    close: list[float]


class BarsProvider(Protocol):
    async def bars(self, symbol: str, years: int) -> Bars | None: ...


class NSEDailyBars:
    """Free NSE daily closes via the signals backtest cache. Fail-open → None."""

    async def bars(self, symbol: str, years: int) -> Bars | None:
        s = await load_series(symbol, years)
        if s is None or not s.dates:
            return None
        return Bars(dates=s.dates, close=s.ohlcv.close)
