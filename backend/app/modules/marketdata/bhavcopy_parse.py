"""Normalize raw NSE archives → typed `BhavRow` bars (pure, no network).

Handles the two official daily formats — the legacy `cm…bhav.csv` (OPEN/CLOSE/TOTTRDVAL, ₹)
and the 2024+ UDiFF `BhavCopy_NSE_CM_…` (OpnPric/ClsPric/TtlTrfVal, ₹) — plus the
`sec_bhavdata_full` 404-fallback (TURNOVER in lakhs, x1e5). Equities only (series EQ/BE); the
caller supplies the ISO `day`, so a row's date never depends on a raw column's date format.
`parse_index_close` reads the NIFTY 50 close from the `ind_close_all_DDMMYYYY.csv` index file.
"""

from __future__ import annotations

import csv
import io

from app.modules.marketdata.bhavcopy_schema import BhavRow

_EQUITY_SERIES = {"EQ", "BE"}
_ALIAS = {
    # legacy cm-bhav daily (plain UPPERCASE → identity once lowercased, except these)
    "tottrdqty": "volume",
    "tottrdval": "turnover",
    # UDiFF (2024+) camelCase
    "tckrsymb": "symbol",
    "sctysrs": "series",
    "opnpric": "open",
    "hghpric": "high",
    "lwpric": "low",
    "clspric": "close",
    "ttltradgvol": "volume",
    "ttltrfval": "turnover",
    # sec_bhavdata_full fallback (turnover in lakhs — converted in `_row`)
    "open_price": "open",
    "high_price": "high",
    "low_price": "low",
    "close_price": "close",
    "ttl_trd_qnty": "volume",
    "turnover_lacs": "turnover_lacs",
}
_FLOATS = ("open", "high", "low", "close", "volume", "turnover")


def _norm(raw: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in raw.items():
        key = k.strip().lower()
        out[_ALIAS.get(key, key)] = (v or "").strip()
    return out


def _row(n: dict[str, str], day: str) -> BhavRow:
    vals = {f: float(n[f]) for f in _FLOATS if n.get(f)}
    if not vals.get("turnover") and n.get("turnover_lacs"):
        vals["turnover"] = float(n["turnover_lacs"]) * 1e5  # lakhs → ₹
    return BhavRow(
        date=day,
        symbol=n["symbol"],
        series=n.get("series") or "EQ",
        isin=n.get("isin", ""),
        **vals,
    )


def parse_raw(text: str, day: str) -> list[BhavRow]:
    """Raw cm-bhav / UDiFF / sec_bhavdata CSV text → equity `BhavRow` bars stamped with `day`."""
    rows: list[BhavRow] = []
    for raw in csv.DictReader(io.StringIO(text)):
        n = _norm(raw)
        if not n.get("symbol"):
            continue
        if (n.get("series") or "EQ") not in _EQUITY_SERIES:
            continue
        rows.append(_row(n, day))
    return rows


def parse_index_close(text: str, name: str = "Nifty 50") -> float | None:
    """Read one index's closing value from an `ind_close_all_DDMMYYYY.csv` file."""
    for raw in csv.DictReader(io.StringIO(text)):
        n = {k.strip().lower(): (v or "").strip() for k, v in raw.items()}
        idx = n.get("index name") or n.get("index_name") or ""
        if idx.lower() == name.lower():
            close = n.get("closing index value") or n.get("close") or ""
            return float(close) if close else None
    return None
