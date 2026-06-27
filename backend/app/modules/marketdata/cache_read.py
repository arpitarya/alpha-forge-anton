"""Read the raw NSE cache with byte-integrity — the verify-on-use Gate-0 for panel-build.

Reads each `eq-{day}.zip` / `idx-{day}.csv` from `nse_data_dir()` (never unzipped to disk) and
**re-hashes it against `cache-manifest.json`**: any mismatch raises `Gate0Error`, so the panel can
never be built on corrupt/partial bytes. Output depends only on the cached bytes, never fetch order.
"""

from __future__ import annotations

from pathlib import Path

from app.modules.marketdata import cache_manifest as cm
from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
from app.modules.marketdata.bhavcopy_integrity import sha256_hex, zip_text
from app.modules.marketdata.bhavcopy_parse import parse_index_close, parse_raw
from app.modules.marketdata.bhavcopy_schema import BhavRow
from app.modules.marketdata.gate0_integrity import Gate0Error
from app.modules.marketdata.panel_utils import BarsByDay


def _verified(man: cm.CacheManifest, path: Path, name: str) -> bytes:
    blob = path.read_bytes()
    e = man.files.get(name)
    if e is None or sha256_hex(blob) != e.sha256:
        raise Gate0Error(f"byte-integrity: {path.name} ≠ cache-manifest sha256 (corrupt cache)")
    return blob


def read_eq_bars(
    frm: str, to: str, man: cm.CacheManifest
) -> tuple[BarsByDay, list[str], list[BhavRow]]:
    bars: BarsByDay = {}
    rows: list[BhavRow] = []
    for path in sorted(nse_data_dir().glob("eq-*.zip")):
        day = path.stem.removeprefix("eq-")
        if not (frm <= day <= to):
            continue
        day_rows = parse_raw(zip_text(_verified(man, path, cm.eq_name(day))), day)
        bars[day] = {r.symbol: r for r in day_rows}
        rows.extend(day_rows)
    return bars, sorted(bars), rows


def read_nifty(dates: list[str], man: cm.CacheManifest) -> list[float]:
    by_day: dict[str, float] = {}
    for path in sorted(nse_data_dir().glob("idx-*.csv")):
        day = path.stem.removeprefix("idx-")
        c = parse_index_close(_verified(man, path, cm.idx_name(day)).decode("utf-8", "replace"))
        if c is not None:
            by_day[day] = c
    series, last = [], 0.0
    for d in dates:
        last = by_day.get(d, last)
        series.append(last)
    return series
