"""Gate 2 for the cross-sectional edge — walk-forward over the 24-config return matrix.

Each config's full weekly-return series is precomputed (so the momentum lookback is never lost to
a slice boundary); we then walk forward over the timeline: on each in-sample window pick the config
with the best expectancy, score *that* config on the next unseen window, roll on. Reuses the gate-2
kill criterion + stats from the single-series engine, so both gates measure identically: PASS iff
aggregate OOS Calmar >= 0.5 AND >= 60% of windows positive (multi-regime by construction).
"""

from __future__ import annotations

from itertools import pairwise

from app.modules.edges.edge_schema import GateResult, ResultStats
from app.modules.edges.edge_stats import build_stats
from app.modules.edges.edge_walkforward import MIN_AGG_CALMAR, MIN_POSITIVE_WINDOW_FRAC

_HOLD = 5  # weekly cadence — annualisation unit for build_stats


def _slices(n_obs: int, n: int) -> list[tuple[int, int]]:
    step = n_obs // n
    return [(k * step, (k + 1) * step) for k in range(n)]


def walk_forward(series_by_cfg: list[list[float]], n_windows: int = 4) -> GateResult:
    """series_by_cfg = one weekly-return series per config (aligned). Gate-2 verdict."""
    if not series_by_cfg:
        return GateResult(gate=2, passed=False, notes=["no config series"])
    n_obs = min(len(s) for s in series_by_cfg)
    slices = _slices(n_obs, n_windows + 1)
    per_window: list[ResultStats] = []
    oos: list[float] = []
    for (lo, hi), (t_lo, t_hi) in pairwise(slices):
        best = max(
            range(len(series_by_cfg)),
            key=lambda c: build_stats(series_by_cfg[c][lo:hi], _HOLD).expectancy_pct,
        )
        seg = series_by_cfg[best][t_lo:t_hi]
        per_window.append(build_stats(seg, _HOLD))
        oos += seg
    agg = build_stats(oos, _HOLD)
    positive = sum(1 for w in per_window if w.expectancy_pct > 0)
    frac = positive / len(per_window) if per_window else 0.0
    passed = agg.calmar >= MIN_AGG_CALMAR and frac >= MIN_POSITIVE_WINDOW_FRAC
    note = f"agg Calmar {agg.calmar} (floor {MIN_AGG_CALMAR}); {positive}/{len(per_window)} wins"
    return GateResult(gate=2, passed=passed, stats=agg, windows=per_window, notes=[note])
