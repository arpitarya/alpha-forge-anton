"""Pure tests for the Phase 5 backtest metrics (§10.5).

No I/O, no network: hand-built round-trips → `build_report`, with the cost math
worked out by hand so a regression in expectancy / win-rate / drawdown / the
friction-vs-STCG split is caught. Headline `net` is cross-checked against the
Phase 4 `realized_pnl` it delegates to.

    uv run pytest tests/test_backtest_metrics.py -v
"""

from __future__ import annotations

from datetime import date

from app.modules.signals.backtest_metrics import build_report
from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg

COSTS = CostsCfg()  # brokerage 20/order, stt 0.1%, friction 0.03%, stcg 20%


def _t(buy: float, sell: float, qty: float, sell_day: int) -> RealizedTrade:
    return RealizedTrade(
        symbol="X",
        qty=qty,
        buy_price=buy,
        sell_price=sell,
        buy_date=date(2024, 1, 1),
        sell_date=date(2024, 1, 1 + sell_day),
    )


# friction_net = gross - 40 - 0.0013*(buy_val+sell_val):
#   A: +500 - 43.25 = 456.75 (win)   B: -100 - 42.47 = -142.47 (loss)   C: +150 - 42.795 = 107.205
_TRADES = [_t(100, 150, 10, 0), _t(100, 90, 10, 1), _t(200, 230, 5, 2)]


def test_empty_window_is_not_a_pass():
    r = build_report([], COSTS)
    assert r.trades == 0 and r.positive_expectancy is False and r.notes


def test_counts_and_win_rate():
    r = build_report(_TRADES, COSTS)
    assert r.trades == 3
    assert r.wins == 2  # A and C net-positive after frictions; B is the loser
    assert r.win_rate == round(2 / 3, 4)


def test_gross_and_headline_net_delegates_to_realized_pnl():
    r = build_report(_TRADES, COSTS)
    assert r.gross == 550.0  # +500 - 100 + 150, pre-cost
    assert r.net == realized_pnl(_TRADES, COSTS).net  # full after-cost incl. STCG


def test_expectancy_and_profit_factor_positive():
    r = build_report(_TRADES, COSTS)
    assert r.expectancy_inr > 0  # mean friction-net per trade is the edge
    assert r.profit_factor > 1  # winners outweigh the loser
    assert r.positive_expectancy is True


def test_max_drawdown_is_the_loser_dip():
    # equity curve ordered by sell_date: 456.75 → 314.28 → 421.485; deepest drop = B's 142.47
    r = build_report(_TRADES, COSTS)
    assert r.max_drawdown == 142.47
    assert 31.0 < r.max_drawdown_pct < 31.4  # 142.47 / 456.75 peak


def test_all_losers_flag_negative_expectancy():
    losers = [_t(100, 80, 10, 0), _t(100, 70, 10, 1)]
    r = build_report(losers, COSTS)
    assert r.positive_expectancy is False and r.net < 0 and r.profit_factor == 0.0
