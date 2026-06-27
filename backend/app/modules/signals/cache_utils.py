"""Resolve the signals on-disk cache dir — `$SIGNALS_CACHE_DIR`, else the home default.

The daily yfinance quotes (`quote_source`) and the once-a-day Nifty-500 list (`universe`) cache to
this dir. It reads `$SIGNALS_CACHE_DIR` (absolute used as-is, `~` expanded) and falls back to
`$ANTON_DATA_DIR/signals-cache` (via `app.core.paths`) when unset. The dir is created on resolve.
"""

from __future__ import annotations

from pathlib import Path

from app.core.paths import resolve as _resolve_path


def signals_cache_dir() -> Path:
    p = _resolve_path("SIGNALS_CACHE_DIR", "signals-cache")
    p.mkdir(parents=True, exist_ok=True)
    return p
