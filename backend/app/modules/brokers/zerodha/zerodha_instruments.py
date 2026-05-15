"""Kite instrument-master cache → tradingsymbol→name/type lookup for Zerodha holdings.

The Kite holdings JSON omits company names and instrument types. This module
fetches the public Kite instruments dump once per TTL to resolve tradingsymbol
→ name and instrument_type (EQ/ETF) when materialising Holding rows.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import csv
import os
import time

from app.core.logging import get_logger
from app.modules.brokers._http import make_client
from app.modules.brokers.dump_utils import dump_dir

logger = get_logger("brokers.zerodha_instruments")

INSTRUMENTS_URL = "https://api.kite.trade/instruments"
_TTL_ENV = "ZERODHA_INSTRUMENTS_TTL_SECONDS"
_DEFAULT_TTL = 24 * 60 * 60
_TRACKED_TYPES = {"EQ", "ETF"}

_NAME_BY_SYMBOL: dict[str, str] | None = None
_TYPE_BY_SYMBOL: dict[str, str] | None = None


def _cache_path():
    return dump_dir() / "zerodha-instruments.csv"


def _ttl() -> int:
    return int(os.getenv(_TTL_ENV, str(_DEFAULT_TTL)))


def _is_fresh() -> bool:
    p = _cache_path()
    return p.exists() and (time.time() - p.stat().st_mtime) < _ttl()


async def _download() -> str:
    async with make_client(base_url="https://api.kite.trade") as client:
        res = await client.get("/instruments")
        res.raise_for_status()
        return res.text


async def _refresh_cache() -> None:
    text = await _download()
    p = _cache_path()
    p.write_text(text, encoding="utf-8")
    os.chmod(p, 0o600)
    logger.info("Zerodha instruments: cached %d bytes → %s", len(text), p)


def _parse_cached() -> tuple[dict[str, str], dict[str, str]]:
    names: dict[str, str] = {}
    types: dict[str, str] = {}
    with _cache_path().open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            itype = (row.get("instrument_type") or "").upper()
            if itype not in _TRACKED_TYPES:
                continue
            sym = (row.get("tradingsymbol") or "").upper().strip()
            if not sym:
                continue
            types.setdefault(sym, itype)
            name = (row.get("name") or "").strip()
            if name:
                names.setdefault(sym, name)
    return names, types


async def _ensure_loaded() -> None:
    global _NAME_BY_SYMBOL, _TYPE_BY_SYMBOL
    if not _is_fresh():
        try:
            await _refresh_cache()
            _NAME_BY_SYMBOL = _TYPE_BY_SYMBOL = None
        except Exception as e:
            logger.warning("Zerodha instruments: refresh failed (%s) — using cache if any", e)
            if not _cache_path().exists():
                _NAME_BY_SYMBOL = _TYPE_BY_SYMBOL = {}
                return
    if _NAME_BY_SYMBOL is None:
        _NAME_BY_SYMBOL, _TYPE_BY_SYMBOL = _parse_cached()
        logger.info(
            "Zerodha instruments: loaded %d names, %d types",
            len(_NAME_BY_SYMBOL), len(_TYPE_BY_SYMBOL or {}),
        )


async def name_lookup() -> dict[str, str]:
    await _ensure_loaded()
    return _NAME_BY_SYMBOL or {}


async def type_lookup() -> dict[str, str]:
    """Return tradingsymbol→instrument_type (EQ/ETF) map."""
    await _ensure_loaded()
    return _TYPE_BY_SYMBOL or {}


def _load_sync() -> None:
    global _NAME_BY_SYMBOL, _TYPE_BY_SYMBOL
    if _NAME_BY_SYMBOL is not None:
        return
    if not _cache_path().exists():
        _NAME_BY_SYMBOL = _TYPE_BY_SYMBOL = {}
        return
    _NAME_BY_SYMBOL, _TYPE_BY_SYMBOL = _parse_cached()


def name_lookup_sync() -> dict[str, str]:
    _load_sync()
    return _NAME_BY_SYMBOL or {}


def type_lookup_sync() -> dict[str, str]:
    _load_sync()
    return _TYPE_BY_SYMBOL or {}
