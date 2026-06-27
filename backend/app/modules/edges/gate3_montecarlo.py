"""Gate 3 — Monte-Carlo outcome cone by seeded block-bootstrap of the weekly returns.

Resampling fixed-length blocks of the realized weekly sleeve returns preserves short-run
autocorrelation (momentum streaks/reversals), unlike an iid draw. We build many forward paths,
emit the p5/p50/p95 cumulative paths + the expected shortfall of the worst 5% finals as a
Phase-0 `Cone`, and KILL when the 5th-percentile path drawdown breaches -20%. Seeded ⇒ the same
returns + seed give the same cone. Scenario-library shocks ride along as red-team context.
"""

from __future__ import annotations

import random

from app.modules.contracts.cone_contract import Cone
from app.modules.edges.scenario_library import scenarios

P5_DRAWDOWN_KILL = -20.0  # the 5th-percentile path max-drawdown must not breach this
_BLOCK = 4


def _bootstrap_path(weekly: list[float], horizon: int, rng: random.Random) -> list[float]:
    out: list[float] = []
    while len(out) < horizon:
        start = rng.randrange(0, max(1, len(weekly) - _BLOCK + 1))
        out += weekly[start : start + _BLOCK]
    cum, s = [], 0.0
    for r in out[:horizon]:
        s += r
        cum.append(round(s, 4))
    return cum


def _max_drawdown(curve: list[float]) -> float:
    peak = dd = 0.0
    for e in curve:
        peak = max(peak, e)
        dd = min(dd, e - peak)
    return dd  # <= 0


def montecarlo_cone(
    weekly: list[float],
    horizon: int = 52,
    n_sims: int = 2000,
    seed: int = 0,
    confidence: float = 0.90,
) -> tuple[Cone, bool, list[str]]:
    """Returns (cone, survives, red_team). survives = P5 path drawdown does not breach -20%."""
    if len(weekly) < _BLOCK:
        return Cone(stale=True), False, ["insufficient history -> honest-pending, no cone"]
    rng = random.Random(seed)  # noqa: S311 — bootstrap resampling, not cryptographic
    sims = [_bootstrap_path(weekly, horizon, rng) for _ in range(n_sims)]
    finals = sorted(p[-1] for p in sims)
    by_final = sorted(sims, key=lambda p: p[-1])
    tail = max(1, int(0.05 * n_sims))
    dd5 = sorted(_max_drawdown(p) for p in sims)[int(0.05 * n_sims)]
    cone = Cone(
        horizon=f"{horizon}w",
        p5=by_final[int(0.05 * n_sims)],
        p50=by_final[n_sims // 2],
        p95=by_final[min(n_sims - 1, int(0.95 * n_sims))],
        es_p5=round(sum(finals[:tail]) / tail, 4),
        confidence=confidence,
    )
    red = [f"{s.name}: {s.equity_shock_pct}%" for s in scenarios()]
    return cone, dd5 >= P5_DRAWDOWN_KILL, red
