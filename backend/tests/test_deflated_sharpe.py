"""Deflated Sharpe — more trials raise the bar; the deflation lowers confidence."""

from __future__ import annotations

from app.modules.edges.deflated_sharpe import deflated_sharpe, expected_max_sharpe, sharpe


def _series() -> list[float]:
    # mildly positive, varied returns over 60 weeks (non-degenerate Sharpe)
    return [0.8 + 0.5 * ((i % 5) - 2) for i in range(60)]


def test_sharpe_positive() -> None:
    assert sharpe(_series()) > 0


def test_expected_max_sharpe_grows_with_trials() -> None:
    assert expected_max_sharpe(0.04, 50) > expected_max_sharpe(0.04, 2) > 0.0
    assert expected_max_sharpe(0.0, 50) == 0.0  # no dispersion across trials → no inflation


def test_more_trials_lowers_dsr() -> None:
    s = _series()
    trials = [sharpe([x + 0.1 * k for x in s]) for k in range(24)]
    dsr_1 = deflated_sharpe(s, trials, 1)
    dsr_24 = deflated_sharpe(s, trials, 24)
    assert 0.0 <= dsr_24 <= dsr_1 <= 1.0
