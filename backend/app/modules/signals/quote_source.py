"""yfinance OHLCV adapter for the signals engine — 12-mo daily, cached once a day.

Maps a broker `tradingsymbol` to a Yahoo symbol (NSE `.NS` / BSE `.BO`, `-EQ`
stripped, small override table), fetches a year of daily bars, and caches them to
disk keyed by symbol+date so a `/signals/review` run is cheap and offline-replayable.
Fail-open: any miss returns None and the ruleset emits HOLD "no data" — never a crash.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

_CACHE = Path.home() / ".alphaforge-anton" / "signals-cache"

# Broker symbol → Yahoo symbol, for the handful that don't follow `SYMBOL.NS`.
_OVERRIDES = {"M&M": "M&M.NS", "M&MFIN": "M&MFIN.NS", "BAJAJ-AUTO": "BAJAJ-AUTO.NS"}


@dataclass
class OHLCV:
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]


def to_yahoo(symbol: str, exchange: str | None = None) -> str:
    if symbol in _OVERRIDES:
        return _OVERRIDES[symbol]
    base = symbol.removesuffix("-EQ").strip().upper()
    suffix = ".BO" if (exchange or "").upper() in ("BSE", "BOM") else ".NS"
    return f"{base}{suffix}"


def _cache_file(yh: str) -> Path:
    return _CACHE / f"{yh}-{date.today().isoformat()}.json"


def _read_cache(yh: str) -> OHLCV | None:
    f = _cache_file(yh)
    if not f.exists():
        return None
    try:
        return OHLCV(**json.loads(f.read_text()))
    except Exception:  # a corrupt cache just forces a refetch
        return None


def _write_cache(yh: str, o: OHLCV) -> None:
    _CACHE.mkdir(parents=True, exist_ok=True)
    _cache_file(yh).write_text(json.dumps(asdict(o)))


def _download(yh: str) -> OHLCV | None:
    import yfinance as yf

    df = yf.Ticker(yh).history(period="1y", interval="1d", auto_adjust=False)
    if df is None or df.empty:
        return None
    return OHLCV(
        high=[float(x) for x in df["High"]],
        low=[float(x) for x in df["Low"]],
        close=[float(x) for x in df["Close"]],
        volume=[float(x) for x in df["Volume"]],
    )


async def daily_ohlcv(symbol: str, exchange: str | None = None) -> OHLCV | None:
    yh = to_yahoo(symbol, exchange)
    if (cached := _read_cache(yh)) is not None:
        return cached
    try:
        o = await asyncio.to_thread(_download, yh)
    except Exception:  # network/symbol error => fail-open HOLD
        return None
    if o is not None:
        _write_cache(yh, o)
    return o
