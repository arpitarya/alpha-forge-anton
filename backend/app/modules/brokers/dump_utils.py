"""Shared CSV-cache utilities for broker holdings dump modules."""
from __future__ import annotations

import csv
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]  # backend/app/modules/brokers/ → alpha-forge/
DEFAULT_DUMP_DIR = Path.home() / ".alphaforge" / "portfolio-dumps"
CSV_HEADERS = (
    "tradingsymbol", "isin", "exchange",
    "quantity", "average_price", "last_price",
    "invested", "current_value", "pnl", "pnl_pct",
)


def dump_dir() -> Path:
    raw = os.getenv("PORTFOLIO_DUMP_DIR", "").strip()
    if raw:
        expanded = Path(raw).expanduser()
        p = expanded if expanded.is_absolute() else (_REPO_ROOT / expanded)
    else:
        p = DEFAULT_DUMP_DIR
    p.mkdir(parents=True, exist_ok=True)
    os.chmod(p, 0o700)
    return p


def live_csv_path(slug: str) -> Path:
    return dump_dir() / f"{slug}-holdings-live.csv"


def dated_csv_path(slug: str) -> Path:
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    return dump_dir() / f"{slug}-holdings-{today}.csv"


def is_csv_fresh(slug: str, ttl_seconds: int) -> bool:
    p = live_csv_path(slug)
    return p.exists() and (time.time() - p.stat().st_mtime) < ttl_seconds


def read_csv(slug: str) -> list[dict[str, str]]:
    with live_csv_path(slug).open(newline="", encoding="utf-8") as fh:
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


def write_csv(rows: list[dict[str, Any]], dst: Path, *, source: str) -> None:
    dumped_at = datetime.now(UTC).isoformat()
    with dst.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# source={source}  dumped_at_utc={dumped_at}  holdings_count={len(rows)}\n")
        w = csv.writer(fh)
        w.writerow(CSV_HEADERS)
        for r in rows:
            w.writerow(_row_values(r))
    os.chmod(dst, 0o600)
