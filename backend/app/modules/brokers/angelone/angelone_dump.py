"""Angel One holdings CSV cache — fetches via SmartAPI, caches to CSV.

TTL controlled by ANGELONE_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.angelone.angelone_dump
    python -m app.modules.brokers.angelone.angelone_dump --force-login
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.angelone.angelone_source_helper import acquire_token, fetch_holdings_json

logger = get_logger("brokers.angelone_dump")
SLUG = "angelone"


def _ttl() -> int:
    return int(os.getenv("ANGELONE_REFETCH_SECONDS", "3600"))


def live_csv_path() -> Path:
    return _du.live_csv_path(SLUG)


def is_csv_fresh() -> bool:
    return _du.is_csv_fresh(SLUG, _ttl())


def read_csv() -> list[dict[str, str]]:
    return _du.read_csv(SLUG)


def write_csv(rows: list[dict[str, Any]], dst: Path) -> None:
    _du.write_csv(rows, dst, source=SLUG)


async def dump_angelone(*, force_login: bool = False) -> Path:
    token = await acquire_token(force=force_login)
    rows = await fetch_holdings_json(token)
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _du.dated_csv_path(SLUG))
    logger.info("Angel One: dumped %d holdings → %s", len(rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_angelone(force_login=force))
    except Exception as e:
        logger.error("Angel One dump failed: %s", e)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
