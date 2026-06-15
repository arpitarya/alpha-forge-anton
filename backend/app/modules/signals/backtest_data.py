"""Multi-year daily OHLCV for the backtest — fetch once, cache, replay offline.

Separate from `quote_source` (which caches a 1-yr window keyed by today for the
live `/review`): the backtest needs N years *with dates* (for STCG short/long
classification) cached by symbol+years. Historical closed bars never change, so a
cached pull makes `just backtest` fully reproducible. Fail-open: a miss → None and
the symbol is skipped, never a crash. Reuses `to_yahoo` for symbol mapping.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from app.modules.signals.quote_source import OHLCV, to_yahoo

_CACHE = Path.home() / ".alphaforge-anton" / "backtest-cache"


@dataclass
class BTSeries:
    dates: list[str]  # ISO trading dates, aligned 1:1 with the OHLCV bars
    ohlcv: OHLCV


def _cache_file(yh: str, years: int) -> Path:
    return _CACHE / f"{yh}-{years}y.json"


def _read_cache(yh: str, years: int) -> BTSeries | None:
    f = _cache_file(yh, years)
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
        return BTSeries(dates=d["dates"], ohlcv=OHLCV(**d["ohlcv"]))
    except Exception:  # a corrupt cache just forces a refetch
        return None


def _write_cache(yh: str, years: int, s: BTSeries) -> None:
    _CACHE.mkdir(parents=True, exist_ok=True)
    payload = {"dates": s.dates, "ohlcv": s.ohlcv.__dict__}
    _cache_file(yh, years).write_text(json.dumps(payload))


def _download(yh: str, years: int) -> BTSeries | None:
    import yfinance as yf

    df = yf.Ticker(yh).history(period=f"{years}y", interval="1d", auto_adjust=False)
    if df is None or df.empty:
        return None
    ohlcv = OHLCV(
        high=[float(x) for x in df["High"]],
        low=[float(x) for x in df["Low"]],
        close=[float(x) for x in df["Close"]],
        volume=[float(x) for x in df["Volume"]],
    )
    return BTSeries(dates=[d.date().isoformat() for d in df.index], ohlcv=ohlcv)


async def load_series(symbol: str, years: int, exchange: str | None = None) -> BTSeries | None:
    yh = to_yahoo(symbol, exchange)
    if (cached := _read_cache(yh, years)) is not None:
        return cached
    try:
        s = await asyncio.to_thread(_download, yh, years)
    except Exception:  # network/symbol error → skip the symbol, never crash
        return None
    if s is not None:
        _write_cache(yh, years, s)
    return s
