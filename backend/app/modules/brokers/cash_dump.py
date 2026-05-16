"""Shared on-disk CSV cache for broker free-cash balances.

One file, one row per broker slug: <dump_dir>/broker-cash-live.csv
Freshness is checked per-row via the stored as_of timestamp — not file
mtime — so each broker's TTL is independent. TTL matches each broker's
refetch_seconds env var (e.g. ZERODHA_REFETCH_SECONDS).
"""

from __future__ import annotations

import csv
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from app.modules.brokers.broker_schemas import WalletBalance
from app.modules.brokers.dump_utils import dump_dir

if TYPE_CHECKING:
    from app.modules.brokers.base import BrokerSource

_FILENAME = "broker-cash-live.csv"
_COLUMNS = ("source", "currency", "cash", "as_of", "available")


def _path() -> Path:
    return dump_dir() / _FILENAME


def _read_all() -> dict[str, dict[str, str]]:
    p = _path()
    if not p.exists():
        return {}
    with p.open(newline="", encoding="utf-8") as fh:
        return {r["source"]: r for r in csv.DictReader(fh)}


def _write_all(rows: dict[str, dict[str, str]]) -> None:
    p = _path()
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_COLUMNS)
        w.writeheader()
        w.writerows(rows.values())
    os.chmod(p, 0o600)


def _row_to_balance(slug: str, row: dict[str, str]) -> WalletBalance | None:
    if row.get("available") != "true":
        return None
    try:
        as_of = datetime.fromisoformat(row["as_of"])
    except (KeyError, ValueError):
        return None
    return WalletBalance(
        source=slug,
        currency=row.get("currency", "INR"),
        cash=float(row.get("cash") or 0),
        as_of=as_of,
        available=True,
    )


def load_cached_cash(slug: str, ttl_seconds: int) -> WalletBalance | None:
    """Return cached WalletBalance if the row exists and is within TTL, else None."""
    if ttl_seconds <= 0:
        return None
    row = _read_all().get(slug)
    if not row:
        return None
    bal = _row_to_balance(slug, row)
    if not bal or not bal.as_of:
        return None
    if (datetime.now(UTC) - bal.as_of).total_seconds() >= ttl_seconds:
        return None
    return bal


def read_cached_cash(slug: str) -> WalletBalance | None:
    """Return persisted WalletBalance regardless of TTL — for display only."""
    row = _read_all().get(slug)
    if not row:
        return None
    return _row_to_balance(slug, row)


def save_cash(bal: WalletBalance) -> None:
    """Upsert one broker's cash row; leaves other brokers' rows untouched."""
    rows = _read_all()
    rows[bal.source] = {
        "source": bal.source,
        "currency": bal.currency,
        "cash": str(round(bal.cash, 2)),
        "as_of": (bal.as_of or datetime.now(UTC)).isoformat(),
        "available": "true" if bal.available else "false",
    }
    _write_all(rows)


async def cached_sync_cash(src: "BrokerSource") -> WalletBalance:
    """Check CSV cache first; only call fetch_cash() if the cache is stale."""
    hit = load_cached_cash(src.slug, src.refetch_seconds)
    if hit:
        return hit
    try:
        bal = await src.fetch_cash()
    except Exception as e:  # noqa: BLE001
        return WalletBalance(source=src.slug, available=False, error=str(e))
    if bal.available:
        save_cash(bal)
    return bal
