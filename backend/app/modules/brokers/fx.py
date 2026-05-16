"""FX helpers — convert holding values to INR before cross-currency sums.

The aggregator mixes INR brokers (Zerodha, Groww, AngelOne) with USD brokers
(IndMoney US stocks). Adding the raw `current_value` understates USD positions
~83×. All cross-currency aggregation must call `to_inr` first.

The USD→INR rate is fetched live from a free public endpoint (open.er-api.com)
and cached on disk for `_TTL_SECONDS` (1 hour). Pattern mirrors `cash_dump.py`
(per-pair row in a single CSV, TTL by stored `as_of`). If the live fetch fails,
we fall back to the last cached value, and finally to `FALLBACK_INR_PER_USD`.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

from app.modules.brokers.dump_utils import dump_dir

logger = logging.getLogger("brokers.fx")

# Static fallback used when the live rate is unavailable and no cache exists.
# Kept in sync with the frontend `wallet.utils.ts` INR_PER_USD constant.
FALLBACK_INR_PER_USD: float = 83.41

_FILENAME = "fx-rates-live.csv"
_COLUMNS = ("pair", "rate", "as_of", "source")
_TTL_SECONDS = 3600
_LIVE_URL = "https://open.er-api.com/v6/latest/USD"
_HTTP_TIMEOUT = 5.0


def _path() -> Path:
    return dump_dir() / _FILENAME


def _read_all() -> dict[str, dict[str, str]]:
    p = _path()
    if not p.exists():
        return {}
    with p.open(newline="", encoding="utf-8") as fh:
        return {r["pair"]: r for r in csv.DictReader(fh)}


def _write_row(pair: str, rate: float, source: str) -> None:
    rows = _read_all()
    rows[pair] = {
        "pair": pair,
        "rate": f"{rate:.6f}",
        "as_of": datetime.now(UTC).isoformat(),
        "source": source,
    }
    p = _path()
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_COLUMNS)
        w.writeheader()
        w.writerows(rows.values())
    os.chmod(p, 0o600)


def _load_cached(pair: str) -> tuple[float, datetime] | None:
    row = _read_all().get(pair)
    if not row:
        return None
    try:
        return float(row["rate"]), datetime.fromisoformat(row["as_of"])
    except (KeyError, ValueError):
        return None


def _fetch_live_usd_inr() -> float:
    """Hit open.er-api.com once. Raises on network/parse failure."""
    req = urllib.request.Request(_LIVE_URL, headers={"User-Agent": "alphaforge-fx/1.0"})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:  # noqa: S310 — trusted https URL
        payload = json.loads(resp.read().decode("utf-8"))
    rate = payload.get("rates", {}).get("INR")
    if not isinstance(rate, (int, float)) or rate <= 0:
        raise ValueError(f"unexpected payload: rates.INR={rate!r}")
    return float(rate)


def get_inr_per_usd() -> float:
    """Return current USD→INR rate, using a 1-hour on-disk cache."""
    pair = "USD/INR"
    cached = _load_cached(pair)
    if cached is not None:
        rate, as_of = cached
        if (datetime.now(UTC) - as_of).total_seconds() < _TTL_SECONDS:
            return rate
    try:
        rate = _fetch_live_usd_inr()
        _write_row(pair, rate, _LIVE_URL)
        return rate
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
        logger.warning("fx: live fetch failed (%s); falling back", e)
        if cached is not None:
            return cached[0]
        return FALLBACK_INR_PER_USD


# Backwards-compat alias — older code/imports referenced the module constant
# directly. Prefer `get_inr_per_usd()` for live values.
INR_PER_USD: float = FALLBACK_INR_PER_USD


def to_inr(value: float, currency: str | None) -> float:
    """Convert `value` from `currency` to INR. Unknown currency is treated as INR."""
    if not currency or currency.upper() in ("INR", ""):
        return value
    if currency.upper() == "USD":
        return value * get_inr_per_usd()
    return value
