"""PBO — a dominant config is not overfit (low); a fit-the-window grid is (high)."""

from __future__ import annotations

from app.modules.edges.cscv_pbo import pbo


def test_dominant_config_has_low_pbo() -> None:
    # config 0 has the best risk-adjusted return everywhere (high mean, low vol); the others
    # hover around zero. The in-sample best is also the OOS best → no overfitting.
    matrix = [[2.0, 1.0] * 32] + [[0.5, -0.5] * 32 for _ in range(7)]
    assert pbo(matrix, n_partitions=8) == 0.0


def test_window_fitting_grid_has_high_pbo() -> None:
    # each config spikes in exactly one partition: whatever looks best in-sample is flat OOS.
    n = 8
    matrix = [[10.0 if t // 8 == k else 0.0 for t in range(64)] for k in range(n)]
    assert pbo(matrix, n_partitions=8) > 0.5


def test_degenerate_inputs() -> None:
    assert pbo([], 8) == 0.0
    assert pbo([[1.0, 2.0]], 8) == 0.0  # <2 configs
