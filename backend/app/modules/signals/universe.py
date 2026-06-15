"""Resolve the screener universe from strategy config — themes or Nifty-500.

`themes` mode takes the union of the configured themes' constituents from the
git-safe `themes.seed.md`. `nifty500` mode pulls the free NSE public CSV and
caches it once a day; if NSE blocks the request or we're offline it **fails open
to the themes universe** so `/signals/screen` still works. Returns plain symbols.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import re
from datetime import date
from pathlib import Path

import httpx
import yaml

from app.modules.signals.strategy_config import StrategyConfig, load_config

logger = logging.getLogger(__name__)

_SEED = Path(__file__).resolve().parent / "themes.seed.md"
_CACHE = Path.home() / ".alphaforge-anton" / "signals-cache"
_NSE_CSV = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _theme_map() -> dict[str, list[str]]:
    if not _SEED.exists():
        return {}
    m = _FRONTMATTER.search(_SEED.read_text())
    return yaml.safe_load(m.group(1) if m else "") or {}


def _themes_universe(themes: list[str]) -> list[str]:
    tmap = _theme_map()
    syms: list[str] = []
    for theme in themes:
        syms.extend(tmap.get(theme, []))
    return sorted(set(syms))


def _nifty500() -> list[str]:
    cache = _CACHE / f"nifty500-{date.today().isoformat()}.json"
    if cache.exists():
        try:
            return json.loads(cache.read_text())
        except Exception as e:  # a corrupt cache just forces a refetch
            logger.debug("nifty500 cache unreadable (%s)", e)
    try:
        resp = httpx.get(_NSE_CSV, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        resp.raise_for_status()
        rows = csv.DictReader(io.StringIO(resp.text))
        syms = sorted({(r.get("Symbol") or "").strip() for r in rows if r.get("Symbol")})
    except Exception as e:  # NSE blocks non-browser fetches sometimes — fail open
        logger.warning("nifty500 fetch failed (%s) — falling back to themes", e)
        return []
    if syms:
        _CACHE.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(syms))
    return syms


def resolve_universe(cfg: StrategyConfig | None = None, theme: str | None = None) -> list[str]:
    cfg = cfg or load_config()
    if theme:  # an explicit ?theme= filter overrides the configured mode
        return _themes_universe([theme])
    if cfg.universe.mode == "nifty500" and (syms := _nifty500()):
        return syms
    return _themes_universe(cfg.universe.themes)
