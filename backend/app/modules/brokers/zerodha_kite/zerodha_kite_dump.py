"""Zerodha holdings CSV cache — fetches via CDP, caches to CSV.

TTL controlled by ZERODHA_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.zerodha_kite.zerodha_kite_dump
    python -m app.modules.brokers.zerodha_kite.zerodha_kite_dump --force-login
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.zerodha_kite.zerodha_kite_instruments import type_lookup_sync
from app.modules.brokers.zerodha_kite.zerodha_kite_source_helper import (
    acquire_enctoken,
    fetch_holdings_json,
)

logger = get_logger("brokers.zerodha_dump")
SLUG = "zerodha"


def _ttl() -> int:
    return int(os.getenv("ZERODHA_REFETCH_SECONDS", "3600"))


def live_csv_path() -> Path:
    return _du.live_csv_path(SLUG)


def is_csv_fresh() -> bool:
    return _du.is_csv_fresh(SLUG, _ttl())


def read_csv() -> list[dict[str, str]]:
    return _du.read_csv(SLUG)


def write_csv(rows: list[dict[str, Any]], dst: Path) -> None:
    _du.write_csv(rows, dst, source=SLUG)


async def dump_zerodha(*, force_login: bool = False) -> Path:
    enctoken = await acquire_enctoken(force=force_login)
    rows = await fetch_holdings_json(enctoken)
    types = type_lookup_sync()
    for r in rows:
        sym = str(r.get("tradingsymbol") or "").upper()
        r.setdefault("asset_class", "etf" if types.get(sym, "EQ").upper() == "ETF" else "equity")
    eq_rows = [r for r in rows if r.get("asset_class") == "equity"]
    live = live_csv_path()
    write_csv(eq_rows, live)
    write_csv(eq_rows, _du.dated_csv_path(SLUG))
    logger.info("Zerodha: dumped %d equity holdings → %s", len(eq_rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_zerodha(force_login=force))
    except Exception as e:
        logger.error("Zerodha dump failed: %s", e)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
