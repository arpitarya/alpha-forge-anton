"""Gate-3 Monte-Carlo cone — seeded determinism, and the P5 -20% drawdown kill."""

from __future__ import annotations

from app.modules.edges.gate3_montecarlo import montecarlo_cone


def test_seeded_cone_is_deterministic() -> None:
    weekly = [0.5, -0.3, 0.8, -0.1, 0.4, -0.6, 0.7, 0.2] * 8
    a = montecarlo_cone(weekly, horizon=20, n_sims=200, seed=7)
    b = montecarlo_cone(weekly, horizon=20, n_sims=200, seed=7)
    assert a[0].model_dump() == b[0].model_dump() and a[1] == b[1]


def test_deeply_negative_series_is_killed() -> None:
    cone, survives, red = montecarlo_cone([-2.0] * 40, horizon=20, n_sims=200, seed=1)
    assert survives is False  # cumulative path breaches -20% well within the horizon
    assert cone.es_p5 < 0 and len(red) == 3  # red-team scenarios attached


def test_rising_series_survives() -> None:
    _, survives, _ = montecarlo_cone([0.5] * 60, horizon=20, n_sims=200, seed=1)
    assert survives is True  # no drawdown → P5 path never breaches -20%


def test_insufficient_history_is_honest_pending() -> None:
    cone, survives, notes = montecarlo_cone([0.1], n_sims=10)
    assert cone.stale is True and survives is False and "honest-pending" in notes[0]
