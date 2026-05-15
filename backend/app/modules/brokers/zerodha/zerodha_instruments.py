"""Kite instrument-master cache → tradingsymbol→name lookup for Zerodha holdings.

The Kite holdings JSON does not include company names. This module fetches
the public Kite instruments dump (https://api.kite.trade/instruments, ~3 MB,
no auth) once per TTL and caches it as a CSV on disk so we can resolve
`tradingsymbol` → `name` when materialising Holding rows.

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
_DEFAULT_TTL = 24 * 60 * 60  # 24h

_NAME_BY_SYMBOL: dict[str, str] | None = None


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


def _parse_cached() -> dict[str, str]:
    """Build tradingsymbol→name map from cached CSV (EQ instruments only)."""
    out: dict[str, str] = {}
    with _cache_path().open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("instrument_type") != "EQ":
                continue
            sym = (row.get("tradingsymbol") or "").upper().strip()
            name = (row.get("name") or "").strip()
            if sym and name:
                out.setdefault(sym, name)
    return out


async def name_lookup() -> dict[str, str]:
    """Return tradingsymbol→name map, refreshing the on-disk cache if stale."""
    global _NAME_BY_SYMBOL
    if not _is_fresh():
        try:
            await _refresh_cache()
            _NAME_BY_SYMBOL = None
        except Exception as e:
            logger.warning("Zerodha instruments: refresh failed (%s) — using cache if any", e)
            if not _cache_path().exists():
                return {}
    if _NAME_BY_SYMBOL is None:
        _NAME_BY_SYMBOL = _parse_cached()
        logger.info("Zerodha instruments: loaded %d EQ names", len(_NAME_BY_SYMBOL))
    return _NAME_BY_SYMBOL


def name_lookup_sync() -> dict[str, str]:
    """Synchronous lookup using the on-disk cache only — never triggers a fetch."""
    global _NAME_BY_SYMBOL
    if _NAME_BY_SYMBOL is not None:
        return _NAME_BY_SYMBOL
    if not _cache_path().exists():
        return {}
    _NAME_BY_SYMBOL = _parse_cached()
    return _NAME_BY_SYMBOL
