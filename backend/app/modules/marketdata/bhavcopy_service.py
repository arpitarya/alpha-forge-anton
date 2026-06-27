"""Per-day NSE ingestion — fetch (or read `--raw-dir`) → validate → atomic-write. Thread-safe.

`ingest_day` is the unit a worker runs: skip if the manifest says the day is already done (byte-
verified), else pull the equity zip + index csv (network via `bhavcopy_fetch`, or a pre-downloaded
`--raw-dir`), validate (zip CRC + parses + NIFTY-50 present), atomic-write both, and return the
records for the caller to merge into the manifest under a lock. No shared mutable state per call.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path

from app.modules.marketdata import bhavcopy_fetch as fetch
from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
from app.modules.marketdata.bhavcopy_integrity import atomic_write, eq_rowcount, idx_ok
from app.modules.marketdata.cache_manifest import CacheManifest, eq_name, idx_name

Record = tuple[str, bytes, str, int]  # (name, blob, source_url, row_count)


class Outcome(StrEnum):
    CACHED = "cached"
    FETCHED = "fetched"
    REFETCHED = "refetched"
    MISSING = "missing"
    FAILED = "failed"


def _raw_bytes(raw_dir: Path, day: str, *, index: bool) -> bytes | None:
    d = date.fromisoformat(day)
    toks = [d.strftime("%Y%m%d"), d.strftime("%d%m%Y"), d.strftime("%d%b%Y").upper()]
    for p in sorted(raw_dir.glob("*")):
        is_idx = "ind_close" in p.name.lower()
        if is_idx == index and any(t in p.name.upper() for t in toks):
            return p.read_bytes()
    return None


def _fetch_eq(opener, day: str) -> tuple[bytes | None, str, int]:
    status = 404
    for url in fetch.eq_urls(day):
        blob, st = fetch.fetch_bytes(opener, url)
        status = st if st != 404 else status
        if blob is not None:
            return blob, url, st
    return None, fetch.eq_urls(day)[0], status


def ingest_day(
    day: str, opener, raw_dir: Path | None, man: CacheManifest
) -> tuple[Outcome, list[Record], int]:
    if man.is_done(day):
        return Outcome.CACHED, [], 200
    had = (nse_data_dir() / eq_name(day)).exists()
    if raw_dir is not None:
        eq, eq_url = _raw_bytes(raw_dir, day, index=False), "raw-dir"
        idx, idx_u, status = _raw_bytes(raw_dir, day, index=True), "raw-dir", 200
    else:
        eq, eq_url, status = _fetch_eq(opener, day)
        idx, ist = fetch.fetch_bytes(opener, fetch.idx_url(day))
        idx_u, status = fetch.idx_url(day), max(status, ist)
    if eq is None:
        return Outcome.MISSING, [], status
    try:
        rows = eq_rowcount(eq, day)
        irows = idx_ok(idx) if idx is not None else 0
    except ValueError:
        return Outcome.FAILED, [], status
    if idx is None:
        return Outcome.FAILED, [], status
    atomic_write(nse_data_dir() / eq_name(day), eq)
    atomic_write(nse_data_dir() / idx_name(day), idx)
    recs = [(eq_name(day), eq, eq_url, rows), (idx_name(day), idx, idx_u, irows)]
    return (Outcome.REFETCHED if had else Outcome.FETCHED), recs, status
