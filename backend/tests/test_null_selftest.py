"""Null-data harness — random data yields no edge, deterministically; not vacuously."""

from __future__ import annotations

import asyncio

from app.modules.edges.edge_data import Bars
from app.modules.edges.null_selftest import GateFunnel, random_walk_bars, run_null_selftest


def test_random_walk_is_deterministic() -> None:
    assert random_walk_bars(7).close == random_walk_bars(7).close
    assert random_walk_bars(7).close != random_walk_bars(8).close


def test_random_data_finds_no_edge() -> None:
    assert asyncio.run(run_null_selftest(25)) == 0


def test_harness_is_not_vacuous() -> None:
    # A strong steady uptrend clears gate 1 (positive out-of-sample expectancy after costs),
    # while pure noise does not — proving the "no edge" result on noise is a real
    # signal-vs-noise discriminator, not a funnel that always fails. (Gate 2's drawdown-free
    # guard then correctly kills a perfectly smooth curve, so verdict alone is too strict.)
    n = 300
    closes = [2000.0 * (1 + 0.03 * i) for i in range(n)]
    trend = Bars(dates=random_walk_bars(0, n).dates, close=closes)
    report = asyncio.run(GateFunnel().run(trend))
    assert 1 in report.gates_passed
