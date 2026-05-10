"""Groww holdings CSV cache — fetches via CDP browser, caches to CSV.

TTL controlled by GROWW_REFETCH_SECONDS (root .env). Default 1h.

Live CSV : ~/.alphaforge/portfolio-dumps/groww-holdings-live.csv
Dated CSV: groww-holdings-YYYY-MM-DD.csv  (archival snapshot, written alongside)

Run standalone:
    python -m app.modules.brokers.groww.dump
    python -m app.modules.brokers.groww.dump --force-login
"""

from __future__ import annotations

import asyncio
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from app.modules.brokers.groww.groww_source_helper import fetch_holdings_via_browser

logger = get_logger("brokers.groww_dump")

DEFAULT_DUMP_DIR = Path.home() / ".alphaforge" / "portfolio-dumps"
CSV_HEADERS = (
    "tradingsymbol", "isin", "exchange",
    "quantity", "average_price", "last_price",
    "invested", "current_value", "pnl", "pnl_pct",
)


def _ttl_seconds() -> int:
    return int(os.getenv("GROWW_REFETCH_SECONDS", "3600"))


def _dump_dir() -> Path:
    raw = os.getenv("PORTFOLIO_DUMP_DIR", "").strip()
    p = Path(raw).expanduser().resolve() if raw else DEFAULT_DUMP_DIR
    p.mkdir(parents=True, exist_ok=True)
    os.chmod(p, 0o700)
    return p


def live_csv_path() -> Path:
    return _dump_dir() / "groww-holdings-live.csv"


def is_csv_fresh() -> bool:
    p = live_csv_path()
    return p.exists() and (time.time() - p.stat().st_mtime) < _ttl_seconds()


def read_csv() -> list[dict[str, str]]:
    with live_csv_path().open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))


def _row_values(r: dict[str, Any]) -> list[Any]:
    qty = float(r.get("quantity") or 0)
    avg = float(r.get("average_price") or 0)
    ltp = float(r.get("last_price") or 0)
    invested, cur = qty * avg, qty * ltp
    pnl = cur - invested
    return [
        r.get("tradingsymbol"), r.get("isin"), r.get("exchange"),
        qty, avg, ltp, round(invested, 2), round(cur, 2),
        round(pnl, 2), round((pnl / invested * 100) if invested else 0.0, 2),
    ]


def write_csv(rows: list[dict[str, Any]], dst: Path) -> None:
    dumped_at = datetime.now(timezone.utc).isoformat()
    with dst.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# source=groww  dumped_at_utc={dumped_at}  holdings_count={len(rows)}\n")
        w = csv.writer(fh)
        w.writerow(CSV_HEADERS)
        for r in rows:
            w.writerow(_row_values(r))
    os.chmod(dst, 0o600)


async def dump_groww(*, force_login: bool = False) -> Path:
    rows = await fetch_holdings_via_browser(force_login=force_login)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    live = live_csv_path()
    write_csv(rows, live)
    write_csv(rows, _dump_dir() / f"groww-holdings-{today}.csv")
    logger.info("Groww: dumped %d holdings → %s", len(rows), live)
    return live


def main() -> int:
    force = "--force-login" in sys.argv
    try:
        path = asyncio.run(dump_groww(force_login=force))
    except Exception as e:
        logger.error("Groww dump failed: %s", e)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
