"""Cross-sectional momentum ranking — the signal at the heart of edge-001.

`momentum_score` is `ret_12_1` generalised: `price[t-skip]/price[t-lookback]-1` (skip the most
recent month so the freshest, mean-reverting bar doesn't pollute the trend). `rank_desc` orders
the whole universe by score (ties broken by symbol for determinism); `select` takes the top
decile/quartile. Pure — no clock, no I/O.
"""

from __future__ import annotations

from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_schema import FactorConfig, Slice

_FRACTION: dict[str, float] = {"decile": 0.10, "quartile": 0.25}


def momentum_score(closes: list[float], t: int, lookback_d: int, skip_d: int) -> float | None:
    """price[t-skip]/price[t-lookback]-1, or None when there isn't enough history."""
    if t - lookback_d < 0 or t - skip_d < 0:
        return None
    past = closes[t - lookback_d]
    if past <= 0:
        return None
    return closes[t - skip_d] / past - 1.0


def rank_desc(panel: Panel, t: int, cfg: FactorConfig) -> list[str]:
    """Universe symbols ranked by momentum descending; ties broken by symbol (deterministic)."""
    scored: list[tuple[float, str]] = []
    for sym in panel.symbols():
        s = momentum_score(panel.closes[sym], t, cfg.lookback_days, cfg.skip_days)
        if s is not None:
            scored.append((s, sym))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [sym for _, sym in scored]


def select(ranked: list[str], slice_: Slice) -> list[str]:
    """Top decile/quartile of the ranked list (at least one name when non-empty)."""
    if not ranked:
        return []
    n = max(1, int(len(ranked) * _FRACTION[slice_]))
    return ranked[:n]
