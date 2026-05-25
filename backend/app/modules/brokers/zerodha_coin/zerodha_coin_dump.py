"""Zerodha Coin MF holdings CSV cache.

TTL controlled by ZERODHA_COIN_REFETCH_SECONDS (root .env). Default 1h.

Run standalone:
    python -m app.modules.brokers.zerodha_coin.zerodha_coin_dump
    python -m app.modules.brokers.zerodha_coin.zerodha_coin_dump --force-login
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
    fetch_holdings_json as fetch_kite_holdings_json,
)
from app.modules.brokers.zerodha_coin.zerodha_coin_source_helper import (
    acquire_token,
    fetch_holdings_json,
)

logger = get_logger("brokers.zerodha_coin_dump")
SLUG = "zerodha_coin"


def _ttl() -> int:
    return int(os.getenv("ZERODHA_COIN_REFETCH_SECONDS", "3600"))


def live_csv_path() -> Path:
    return _du.live_csv_path(SLUG)


def is_csv_fresh() -> bool:
    return _du.is_csv_fresh(SLUG, _ttl())


def read_csv() -> list[dict[str, str]]:
    return _du.read_csv(SLUG)


def write_csv(rows: list[dict[str, Any]], dst: Path) -> None:
    _du.write_csv(rows, dst, source=SLUG)


async def dump_zerodha_coin(*, force_login: bool = False) -> Path:
    token = await acquire_token(force=force_login)
    mf_rows = await fetch_holdings_json(token)
    for r in mf_rows:
        r.setdefault("name", r.get("fund", ""))
        r.setdefault("asset_class", "mutual_fund")

    etf_rows: list[dict] = []
    try:
        enctoken = await acquire_enctoken(force=force_login)
        kite_rows = await fetch_kite_holdings_json(enctoken)
        types = type_lookup_sync()
        for r in kite_rows:
            sym = str(r.get("tradingsymbol") or "").upper()
            if types.get(sym, "EQ").upper() == "ETF":
                r.setdefault("asset_class", "etf")
                etf_rows.append(r)
    except Exception as e:
        logger.warning("Zerodha Coin dump: ETF fetch failed (%s) — MF only", e)

    all_rows = etf_rows + mf_rows
    live = live_csv_path()
    write_csv(all_rows, live)
    write_csv(all_rows, _du.dated_csv_path(SLUG))
    logger.info("Zerodha Coin: dumped %d ETF + %d MF holdings → %s", len(etf_rows), len(mf_rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_zerodha_coin(force_login=force))
    except Exception as e:
        logger.error("Zerodha Coin dump failed: %s", e)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
