"""Wint Wealth holdings CSV cache.

TTL controlled by WINTWEALTH_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.wintwealth.wintwealth_dump
    python -m app.modules.brokers.wintwealth.wintwealth_dump --force-login
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import app.modules.brokers.dump_utils as _du
from app.core.logging import get_logger
from app.modules.brokers.wintwealth.wintwealth_source_helper import fetch_holdings_via_browser

logger = get_logger("brokers.wintwealth_dump")
SLUG = "wintwealth"


def _ttl() -> int:
    return int(os.getenv("WINTWEALTH_REFETCH_SECONDS", "3600"))


def live_csv_path() -> Path:
    return _du.live_csv_path(SLUG)


def is_csv_fresh() -> bool:
    return _du.is_csv_fresh(SLUG, _ttl())


def read_csv() -> list[dict[str, str]]:
    return _du.read_csv(SLUG)


def write_csv(rows: list[dict[str, Any]], dst: Path) -> None:
    _du.write_csv(rows, dst, source=SLUG)


async def dump_wintwealth(*, force_login: bool = False) -> Path:
    rows = await fetch_holdings_via_browser(force_login=force_login)
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _du.dated_csv_path(SLUG))
    logger.info("WintWealth: dumped %d holdings → %s", len(rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_wintwealth(force_login=force))
    except Exception as e:
        logger.error("WintWealth dump failed: %s", e)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
