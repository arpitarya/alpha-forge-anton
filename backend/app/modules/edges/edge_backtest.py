"""Gate 1 — deterministic out-of-sample backtest of a pre-registered edge. Pure.

Generates fixed-holding-period round-trips from the spec's signal over its universe,
nets each via `edge_costs`, and builds `ResultStats`. Determinism: symbols are sorted,
there is no clock, and the round-trip generator + stats builder are the shared
primitives gate 2 (`edge_walkforward`) reuses, so both gates measure identically.

Gate 1 splits each symbol's bars into an in-sample head and an out-of-sample tail and
scores **only the out-of-sample tail** — an edge that needs the bars it was written on
is not an edge. Entry params default to the signal's first grid point (gate 2 tunes them).
"""

from __future__ import annotations

from datetime import date

from app.modules.edges.edge_costs import net_pct
from app.modules.edges.edge_data import Bars, BarsProvider
from app.modules.edges.edge_schema import EdgeSpec, GateResult
from app.modules.edges.edge_signal import get_signal, param_grid
from app.modules.edges.edge_stats import build_stats
from app.modules.signals.strategy_config import CostsCfg

OOS_FRACTION = 0.30  # last 30% of each symbol's history is held out for gate 1


def round_trips(
    b: Bars, signal: str, params: tuple[int, ...], hold: int, lo: int, hi: int, costs: CostsCfg
) -> list[float]:
    """Net % per round-trip: enter when the signal fires in [lo, hi), exit `hold` bars later."""
    fire = get_signal(signal)
    out: list[float] = []
    i = lo
    while i + hold < hi:
        if fire(b.close, i, params):
            out.append(
                net_pct(
                    b.close[i],
                    b.close[i + hold],
                    1.0,
                    date.fromisoformat(b.dates[i]),
                    date.fromisoformat(b.dates[i + hold]),
                    costs,
                )
            )
            i += hold  # one position per symbol at a time — non-overlapping
        else:
            i += 1
    return out


async def _series(spec: EdgeSpec, provider: BarsProvider, years: int) -> list[Bars]:
    bars: list[Bars] = []
    for sym in sorted(spec.universe):
        if (b := await provider.bars(sym, years)) is not None and b.dates:
            bars.append(b)
    return bars


async def run_gate1(
    spec: EdgeSpec, provider: BarsProvider, costs: CostsCfg | None = None, years: int = 5
) -> GateResult:
    costs = costs or CostsCfg()
    params = (param_grid(spec.signal) or [()])[0]
    hold = spec.holding_period_days
    nets: list[float] = []
    for b in await _series(spec, provider, years):
        split = int(len(b.close) * (1 - OOS_FRACTION))
        nets += round_trips(b, spec.signal, params, hold, split, len(b.close), costs)
    stats = build_stats(nets, hold)
    passed = stats.trades > 0 and stats.expectancy_pct > 0
    note = "positive out-of-sample expectancy" if passed else "no out-of-sample edge after costs"
    return GateResult(gate=1, passed=passed, stats=stats, notes=[note])
