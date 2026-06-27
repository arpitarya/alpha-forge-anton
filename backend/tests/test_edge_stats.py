"""edge_stats — the implausible-drawdown guard (no network, pure).

A drawdown-free curve over a meaningful sample is overfit/look-ahead, not a flawless
edge: it must score Calmar 0 (fail the gate), never a large positive. The epsilon only
guards a true divide-by-zero on genuinely tiny (low-confidence) samples.

    uv run pytest tests/test_edge_stats.py -v
"""

from __future__ import annotations

from app.modules.edges.edge_stats import _MIN_TRADES_NO_DD, build_stats


def test_drawdown_free_over_meaningful_sample_fails() -> None:
    # All wins, monotonically rising cumulative curve ⇒ zero drawdown, many trades.
    nets = [1.0] * (_MIN_TRADES_NO_DD + 5)
    s = build_stats(nets, hold_days=5)
    assert s.max_dd_pct == 0.0
    assert s.calmar == 0.0, "drawdown-free run over a big sample must fail, not ace, the gate"


def test_tiny_drawdown_free_sample_still_computes() -> None:
    # Below the trade threshold: epsilon guards divide-by-zero (low confidence, but not zeroed).
    nets = [1.0, 1.0, 1.0]
    s = build_stats(nets, hold_days=5)
    assert s.calmar != 0.0


def test_normal_run_with_drawdown_unaffected() -> None:
    # A real curve that dips (a loss after gains) keeps a finite, non-zeroed Calmar.
    nets = [2.0, -1.0, 2.0, -1.0] * 5
    s = build_stats(nets, hold_days=5)
    assert s.max_dd_pct > 0.0
    assert s.calmar != 0.0


def test_weekly_portfolio_series_is_scored_identically() -> None:
    # The cross-sectional funnel feeds a WEEKLY portfolio-return series into the same
    # build_stats (hold_days=5). A series with pullbacks scores a finite positive Calmar;
    # a drawdown-free weekly run still trips the guard — both gates measure identically.
    weekly = [1.5, 1.5, -1.0] * 10
    s = build_stats(weekly, hold_days=5)
    assert s.max_dd_pct > 0.0 and s.calmar > 0.0
    assert build_stats([0.7] * 30, hold_days=5).calmar == 0.0
