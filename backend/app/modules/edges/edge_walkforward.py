"""Gate 2 — walk-forward validation. Optimise on one window, test on the next unseen.

The discipline gate 1 can't enforce: an edge must survive parameters chosen *without*
seeing the test bars. We split history into `n_windows+1` contiguous slices; for each
adjacent pair we pick the best param point on slice k (in-sample) and score it on slice
k+1 (out-of-sample), rolling forward. We report per-window stats and the aggregate.

Kill criterion (slice-1 constants — changed ONLY by an explicit, logged decision, not
config knobs): pass iff aggregate out-of-sample Calmar ≥ 0.5 AND ≥ 60% of test windows
have positive expectancy. An edge tuned to one regime fails the 60% consistency floor.
"""

from __future__ import annotations

from itertools import pairwise

from app.modules.edges.edge_backtest import _series, round_trips
from app.modules.edges.edge_data import Bars, BarsProvider
from app.modules.edges.edge_schema import EdgeSpec, GateResult, ResultStats
from app.modules.edges.edge_signal import param_grid
from app.modules.edges.edge_stats import build_stats
from app.modules.signals.strategy_config import CostsCfg

MIN_AGG_CALMAR = 0.5  # aggregate out-of-sample Calmar floor
MIN_POSITIVE_WINDOW_FRAC = 0.60  # ≥ 60% of test windows must be net-positive


def _bounds(length: int, n_slices: int) -> list[tuple[int, int]]:
    step = length // n_slices
    return [(k * step, (k + 1) * step) for k in range(n_slices)]


def _best_params(bars: list[Bars], signal: str, lo: int, hi: int, hold: int, costs: CostsCfg):
    """Pick the grid point with the highest in-sample expectancy on [lo, hi)."""
    best, best_exp = (param_grid(signal) or [()])[0], float("-inf")
    for p in param_grid(signal) or [()]:
        nets = [x for b in bars for x in round_trips(b, signal, p, hold, lo, hi, costs)]
        exp = build_stats(nets, hold).expectancy_pct
        if exp > best_exp:
            best, best_exp = p, exp
    return best


async def run_gate2(
    spec: EdgeSpec,
    provider: BarsProvider,
    costs: CostsCfg | None = None,
    years: int = 5,
    n_windows: int = 4,
) -> GateResult:
    costs = costs or CostsCfg()
    bars = await _series(spec, provider, years)
    length = min((len(b.close) for b in bars), default=0)
    slices = _bounds(length, n_windows + 1)
    hold = spec.holding_period_days

    per_window: list[ResultStats] = []
    oos_nets: list[float] = []  # concatenated test-window nets → the aggregate
    for (lo, hi), (t_lo, t_hi) in pairwise(slices):
        params = _best_params(bars, spec.signal, lo, hi, hold, costs)  # in-sample fit
        nets = [
            x for b in bars for x in round_trips(b, spec.signal, params, hold, t_lo, t_hi, costs)
        ]
        per_window.append(build_stats(nets, hold))
        oos_nets += nets

    agg = build_stats(oos_nets, hold)
    positive = sum(1 for w in per_window if w.expectancy_pct > 0)
    frac = positive / len(per_window) if per_window else 0.0
    passed = agg.calmar >= MIN_AGG_CALMAR and frac >= MIN_POSITIVE_WINDOW_FRAC
    note = (
        f"agg Calmar {agg.calmar} (≥{MIN_AGG_CALMAR}?), "
        f"{positive}/{len(per_window)} windows positive (≥{MIN_POSITIVE_WINDOW_FRAC:.0%}?)"
    )
    return GateResult(gate=2, passed=passed, stats=agg, windows=per_window, notes=[note])
