"""Zerodha holdings CSV cache — fetches via CDP, caches to CSV.

TTL controlled by ZERODHA_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.zerodha.zerodha_dump
    python -m app.modules.brokers.zerodha.zerodha_dump --force-login
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.zerodha.zerodha_source_helper import (
    acquire_enctoken,
    fetch_holdings_json,
    fetch_mf_holdings_json,
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
    try:
        mf_rows = await fetch_mf_holdings_json(enctoken)
        for r in mf_rows:
            r["name"] = r.get("fund", "")
            r.setdefault("asset_class", "mutual_fund")
        rows = rows + mf_rows
    except Exception as e:
        logger.warning("Zerodha COIN: MF dump failed (%s) — equity/ETF only", e)
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _du.dated_csv_path(SLUG))
    logger.info("Zerodha: dumped %d holdings → %s", len(rows), live)
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
