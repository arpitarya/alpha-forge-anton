"""Gate 1 — known-answer + byte-identical determinism (no network).

A controlled fixture: a flat ₹100 series with a single ₹110 bump exactly 5 bars after
each `overfit_dayofmonth(k=0)` fire (i = 0, 7, 14, …). Every round-trip is therefore
the *same* buy=100 → sell=110, qty=1, 5-day hold. Its net after costs is the hand-
checked figure from test_edge_costs (qty=1: brokerage dominates → -32.375%). So the
gate-1 expectancy is exactly -32.375% and reruns must be byte-identical.

    uv run pytest tests/test_edge_backtest.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.edges.edge_backtest import run_gate1
from app.modules.edges.edge_data import Bars
from app.modules.edges.edge_schema import EdgeSpec

_N = 40
_RUN_AT = datetime(2026, 6, 21, tzinfo=UTC)


class _FixtureBars:
    """Offline provider: one symbol, flat 100 with a +10 bump 5 bars after each fire."""

    def __init__(self) -> None:
        closes = [100.0] * _N
        for fire in range(0, _N, 7):
            if (j := fire + 5) < _N:
                closes[j] = 110.0
        self._b = Bars(dates=[f"2024-01-{(i % 28) + 1:02d}" for i in range(_N)], close=closes)

    async def bars(self, symbol: str, years: int) -> Bars:
        return self._b


def _spec() -> EdgeSpec:
    return EdgeSpec(
        id="edge-known",
        hypothesis="known-answer fixture",
        universe=["X"],
        signal="overfit_dayofmonth",
        holding_period_days=5,
        pre_registered_at=_RUN_AT,
    )


@pytest.mark.asyncio
async def test_gate1_known_answer_expectancy_is_exact():
    # OOS_FRACTION holds out the last 30%; full-history fire count drops, but every
    # scored trip is the identical -32.375% round-trip, so expectancy is exact.
    r = await run_gate1(_spec(), _FixtureBars())
    assert r.stats.trades >= 1
    assert r.stats.expectancy_pct == -32.375  # byte-exact hand-checked net


@pytest.mark.asyncio
async def test_gate1_is_byte_identical_across_runs():
    a = await run_gate1(_spec(), _FixtureBars())
    b = await run_gate1(_spec(), _FixtureBars())
    assert a.model_dump_json() == b.model_dump_json()


@pytest.mark.asyncio
async def test_gate1_kills_a_negative_edge():
    r = await run_gate1(_spec(), _FixtureBars())
    assert r.passed is False  # -32% expectancy → no edge after costs
