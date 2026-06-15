"""ta-lib indicator wrappers — reduce a year of OHLCV to the scalars the ruleset
needs. Pure compute, no I/O. Returns None when there aren't enough bars to trust
the slow averages (the caller then emits HOLD "no data")."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import talib

from app.modules.signals.quote_source import OHLCV

_MIN_BARS = 60  # enough for DMA50 + a stable ADX/ATR
_RECENT_HIGH_WIN = 22  # ~1 trading month, the trailing-stop anchor
_YEAR = 252


@dataclass
class Indicators:
    close: float
    rsi14: float
    adx14: float
    dma50: float
    dma200: float
    atr14: float
    recent_high: float  # max high over the last ~month (trailing-stop reference)
    pos_52w: float  # 0..1 position within the 52-week range
    vol_ratio: float  # last volume / 20-day average


def _last(arr: np.ndarray) -> float:
    clean = arr[~np.isnan(arr)]
    return float(clean[-1]) if clean.size else 0.0


def compute(o: OHLCV) -> Indicators | None:
    close = np.asarray(o.close, dtype=float)
    high = np.asarray(o.high, dtype=float)
    low = np.asarray(o.low, dtype=float)
    vol = np.asarray(o.volume, dtype=float)
    if close.size < _MIN_BARS:
        return None
    win = min(_YEAR, close.size)
    hi, lo = float(np.max(high[-win:])), float(np.min(low[-win:]))
    avg_vol = float(np.mean(vol[-20:])) or 1.0
    return Indicators(
        close=float(close[-1]),
        rsi14=_last(talib.RSI(close, 14)),
        adx14=_last(talib.ADX(high, low, close, 14)),
        dma50=_last(talib.SMA(close, 50)),
        dma200=_last(talib.SMA(close, min(200, close.size))),
        atr14=_last(talib.ATR(high, low, close, 14)),
        recent_high=float(np.max(high[-_RECENT_HIGH_WIN:])),
        pos_52w=round((float(close[-1]) - lo) / (hi - lo), 4) if hi > lo else 0.0,
        vol_ratio=round(float(vol[-1]) / avg_vol, 2),
    )
