"""Gate 2 — the discipline that gate 1 cannot enforce (no network).

The acceptance criterion: a deliberately **overfit** toy edge PASSES gate 1 but is
REJECTED at gate 2. The trap uses `overfit_dayofmonth` on a fixture where the default
weekday (k=0) is engineered to win on gate-1's held-out tail, while across the four
walk-forward windows the in-sample optimiser chases a *different* lucky weekday each
time that does not carry over — so out-of-sample expectancy is negative in every window
(0/4 positive, Calmar < 0). To prove gate 2 isn't a rubber stamp, a genuinely stable
`momentum` edge on a steady uptrend passes BOTH gates.

    uv run pytest tests/test_edge_walkforward.py -v
"""

from __future__ import annotations

import math

import pytest

from app.modules.edges.edge_backtest import OOS_FRACTION, run_gate1
from app.modules.edges.edge_data import Bars
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.edges.edge_walkforward import run_gate2


def _provider(b: Bars):
    class _P:
        async def bars(self, symbol: str, years: int) -> Bars:
            return b

    return _P()


def _overfit_bars() -> Bars:
    """k=0 wins on the gate-1 tail; earlier windows reward a rotating, non-carrying k."""
    n, px = 280, 2000.0  # high price → flat brokerage is negligible, % move shows through
    closes = [px] * n
    tail, slice_len = int(n * (1 - OOS_FRACTION)), n // 5
    for i in range(n):
        if i + 5 >= n:
            continue
        if i >= tail:
            if i % 7 == 0:
                closes[i + 5] = closes[i] * 1.05  # k=0 wins the held-out tail → G1 passes
        else:
            lucky = (i // slice_len * 3) % 7
            if i % 7 == lucky:
                closes[i + 5] = closes[i] * 1.04
            elif i % 7 == (lucky + 2) % 7:
                closes[i + 5] = closes[i] * 0.95
    return Bars(
        dates=[f"2024-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)], close=closes
    )


def _real_bars() -> Bars:
    n, px = 300, 2000.0
    # uptrend with pullbacks → a real (small) drawdown, so the ca6b3fd Calmar-0 guard
    # accepts it (a monotonic line scores Calmar 0 and would wrongly fail gate 2).
    closes = [px * (1.004**i) * (1.0 + 0.04 * math.sin(i / 5.0)) for i in range(n)]
    return Bars(
        dates=[f"2024-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)], close=closes
    )


def _spec(signal: str) -> EdgeSpec:
    return EdgeSpec(id="e", hypothesis="h", universe=["X"], signal=signal, holding_period_days=5)


@pytest.mark.asyncio
async def test_overfit_edge_passes_gate1_but_is_killed_at_gate2():
    p = _provider(_overfit_bars())
    g1 = await run_gate1(_spec("overfit_dayofmonth"), p)
    g2 = await run_gate2(_spec("overfit_dayofmonth"), p)
    assert g1.passed is True  # looks like an edge in-sample / on the tail
    assert g2.passed is False  # walk-forward exposes it
    assert sum(1 for w in g2.windows if w.expectancy_pct > 0) / len(g2.windows) < 0.60


@pytest.mark.asyncio
async def test_genuine_edge_clears_both_gates():
    p = _provider(_real_bars())
    assert (await run_gate1(_spec("momentum"), p)).passed is True
    g2 = await run_gate2(_spec("momentum"), p)
    assert g2.passed is True and g2.stats.calmar >= 0.5


@pytest.mark.asyncio
async def test_gate2_is_byte_identical_across_runs():
    a = await run_gate2(_spec("overfit_dayofmonth"), _provider(_overfit_bars()))
    b = await run_gate2(_spec("overfit_dayofmonth"), _provider(_overfit_bars()))
    assert a.model_dump_json() == b.model_dump_json()
