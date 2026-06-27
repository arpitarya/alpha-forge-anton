"""Weekly simulator — exit rules fire, and the net-return series is deterministic."""

from __future__ import annotations

from app.modules.edges.factor_exits import leg_exit
from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_quality import FixtureFundamentals
from app.modules.edges.factor_rebalance import simulate
from app.modules.edges.factor_schema import FactorConfig


def _dates(n: int) -> list[str]:
    return [f"2024-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)]


def test_leg_exit_guard_then_stop() -> None:
    cfg = FactorConfig(stop_on=True)
    # enter at index 5 (100); index 6 is -21% → the hard guard fires first
    ex, reason = leg_exit([100.0] * 6 + [79.0, 80.0], 5, 5, cfg)
    assert (ex, reason) == (6, "guard_-20pct")
    # no guard breach, but a close below the prior 20-day low → stop
    rising = [100.0 + i for i in range(6)] + [90.0]
    ex2, reason2 = leg_exit(rising, 5, 5, cfg)
    assert reason2 == "20d_low_stop" and ex2 == 6


def _panel(n: int, n_syms: int = 20) -> Panel:
    closes = {f"S{k:02d}": [100.0 * (1 + 0.0005 * t) for t in range(n)] for k in range(n_syms)}
    return Panel(dates=_dates(n), closes=closes, nifty=[0.0] * n)


def test_simulate_is_deterministic_and_counts_pending() -> None:
    cfg = FactorConfig(lookback_months=1, skip_month=False, trend_on=False, slice="decile")
    panel = _panel(40)
    # S00 (a selected name) has unknown fundamentals → honest-pending each week
    fund = FixtureFundamentals(
        roce={f"S{k:02d}": 20.0 for k in range(1, 20)},
        debt_equity={f"S{k:02d}": 0.3 for k in range(1, 20)},
    )
    a = simulate(panel, cfg, fund)
    b = simulate(panel, cfg, fund)
    assert a == b  # same panel + config ⇒ identical series
    assert len(a.weekly) > 0
    assert a.pending > 0  # S00 selected but unscreenable → surfaced, not faked in
