"""Point-in-time liquidity membership — the eligible cross-section at each rebalance.

`liquid_as_of(panel, t)` is the top-N symbols by trailing-`window` median ₹ turnover ending at
bar `t`, minus the **runtime** never-buy exclusions (symbols + a point-in-time price floor). The
hard list is an elgar money doc, so anton holds only the loader (`load_exclusions`) and a scoped
module-active set, NEVER the tickers. Because turnover is 0 on non-trading days
(`panel_universe.align_turnover` never forward-fills), a not-yet-listed or already-delisted name
has a zero trailing median and is excluded — survivorship-safe and look-ahead-free by construction.
With no turnover (synthetic fixture) and no exclusions it falls back to the full symbol set, so the
existing offline EB-0 run stays byte-identical.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path

from app.modules.edges.factor_panel import Panel

TOP_N = 250  # eligible cross-section width (locked: top ~250 by liquidity)
WINDOW = 60  # trailing sessions for the median-turnover rank


@dataclass(frozen=True)
class Exclusions:
    """Runtime never-buy filter loaded from an off-repo elgar doc — tickers never live in anton."""

    symbols: frozenset[str] = field(default_factory=frozenset)
    price_floor_inr: float = 0.0  # drop names whose point-in-time close at t is below this
    source: str = "none"  # provenance label for the TestReport (count + source, never tickers)


NO_EXCLUSIONS = Exclusions()  # the empty singleton (use as a default arg; never mutate)
_ACTIVE = NO_EXCLUSIONS  # scoped by run_funnel / build (set→restore); default empty ⇒ no-op


def active() -> Exclusions:
    return _ACTIVE


def set_active(e: Exclusions) -> Exclusions:
    """Set the active exclusions; returns the previous so callers can restore (test isolation)."""
    global _ACTIVE
    prev, _ACTIVE = _ACTIVE, e
    return prev


def load_exclusions(path: Path) -> Exclusions:
    """Load {"symbols":[…], "price_floor_inr": int} from an off-repo elgar path."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Exclusions(
        symbols=frozenset(d.get("symbols", [])),
        price_floor_inr=float(d.get("price_floor_inr", 0) or 0),
        source=Path(path).stem,
    )


def liquid_as_of(panel: Panel, t: int, top_n: int = TOP_N, window: int = WINDOW) -> list[str]:
    """Eligible symbols at bar `t`: top-N by trailing-`window` median turnover, minus exclusions."""
    excl = _ACTIVE
    if not panel.turnover:  # synthetic fixture → full universe (preserves determinism)
        return [s for s in panel.symbols() if s not in excl.symbols]
    lo = max(0, t - window + 1)
    med: dict[str, float] = {}
    for sym, series in panel.turnover.items():
        if sym in excl.symbols or t >= len(series) or series[t] <= 0:
            continue  # must be trading AT t — excludes pre-listing / post-delisting names
        closes = panel.closes.get(sym)
        if excl.price_floor_inr and (not closes or closes[t] < excl.price_floor_inr):
            continue  # sub-floor at t — point-in-time close only (no look-ahead)
        window_vals = series[lo : t + 1]
        m = statistics.median(window_vals) if window_vals else 0.0
        if m > 0:
            med[sym] = m
    return sorted(med, key=lambda s: (-med[s], s))[:top_n]
