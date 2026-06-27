"""Ingest NSE bhavcopy CSVs into a cache, and derive the point-in-time universe.

Reuses the broker `dump_utils` I/O discipline — `dump_dir()` (chmod 700), a chmod-600
write, and the `# source=…` header-comment — but defines its own OHLCV column set rather
than the holdings `CSV_HEADERS` (a bhavcopy bar is not a holding). Parsing accepts the
common raw NSE header aliases (OPEN_PRICE, TOTTRDQTY, TIMESTAMP, …) so a real dump and our
normalized cache both load. `universe_as_of` is the only honest, look-ahead-free universe.
"""

from __future__ import annotations

import csv
import os
from datetime import UTC, datetime
from pathlib import Path

from app.modules.brokers.dump_utils import dump_dir
from app.modules.marketdata.bhavcopy_schema import BhavRow, UniverseSnapshot

_COLUMNS = ("date", "symbol", "series", "isin", "open", "high", "low", "close", "volume")
_ALIAS = {
    "open_price": "open",
    "high_price": "high",
    "low_price": "low",
    "close_price": "close",
    "last_price": "close",
    "tottrdqty": "volume",
    "ttl_trd_qnty": "volume",
    "timestamp": "date",
    "date1": "date",
}
_FLOATS = ("open", "high", "low", "close", "volume")


def _key(header: str) -> str:
    k = header.strip().lower()
    return _ALIAS.get(k, k)


def _to_row(raw: dict[str, str], day: str | None) -> BhavRow:
    r = {_key(k): (v or "").strip() for k, v in raw.items()}
    vals = {f: float(r[f]) for f in _FLOATS if r.get(f)}
    return BhavRow(
        date=r.get("date") or day or "",
        symbol=r["symbol"],
        series=r.get("series") or "EQ",
        isin=r.get("isin") or "",
        **vals,
    )


def parse_bhavcopy(path: Path, day: str | None = None) -> list[BhavRow]:
    """Parse a raw or normalized bhavcopy CSV; `day` supplies the date if no column has it."""
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(ln for ln in fh if not ln.startswith("#"))
        return [_to_row(raw, day) for raw in reader if (raw.get("SYMBOL") or raw.get("symbol"))]


def cache_path(day: str) -> Path:
    return dump_dir() / f"bhavcopy-{day}.csv"


def write_bhavcopy(rows: list[BhavRow], day: str) -> Path:
    """Cache normalized rows with the dump_utils header-comment + chmod 600."""
    dst = cache_path(day)
    stamp = datetime.now(UTC).isoformat()
    with dst.open("w", newline="", encoding="utf-8") as fh:
        fh.write(f"# source=bhavcopy  dumped_at_utc={stamp}  rows={len(rows)}\n")
        w = csv.writer(fh)
        w.writerow(_COLUMNS)
        for r in rows:
            w.writerow([getattr(r, c) for c in _COLUMNS])
    os.chmod(dst, 0o600)
    return dst


def universe_as_of(rows: list[BhavRow], as_of: str) -> UniverseSnapshot:
    """Symbols trading on the latest session on/before `as_of` — no look-ahead."""
    sessions = sorted({r.date for r in rows if r.date and r.date <= as_of})
    if not sessions:
        return UniverseSnapshot(as_of=as_of, symbols=[])
    pinned = sessions[-1]
    symbols = sorted({r.symbol for r in rows if r.date == pinned})
    return UniverseSnapshot(as_of=as_of, symbols=symbols)
