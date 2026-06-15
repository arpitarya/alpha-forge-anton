"""Unit tests for the monthly realized-P&L tracker (handoff §10.4).

Pure: feed closed round-trips + the default cost knobs and assert each component
(brokerage / STT / friction / STCG) and the net, plus ST-vs-LT classification and
ST-loss-offset. Costs come from `CostsCfg` defaults (config-driven, not hardcoded).

    uv run pytest tests/test_pnl_tracker.py -v
"""

from __future__ import annotations

from datetime import date

from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg

COSTS = CostsCfg()  # brokerage 20/order, stt 0.1%, friction 0.03%, stcg 20%


def _t(buy: float, sell: float, qty: float = 10, days: int = 59) -> RealizedTrade:
    return RealizedTrade(
        symbol="X",
        qty=qty,
        buy_price=buy,
        sell_price=sell,
        buy_date=date(2026, 1, 1),
        sell_date=date(2026, 1, 1) + _delta(days),
    )


def _delta(days: int):
    from datetime import timedelta

    return timedelta(days=days)


def test_short_term_components_and_net():
    r = realized_pnl([_t(100, 150)], COSTS, target=300)
    assert r.gross == 500.0  # (150-100)*10
    assert r.brokerage == 40.0  # 2 orders * 20
    assert r.stt == 2.5  # 0.1% * (1000+1500)
    assert r.friction == 0.75  # 0.03% * 2500
    assert r.stcg == 100.0  # 20% * 500 short-term gain
    assert r.net == 356.75 and r.vs_target == 56.75


def test_long_term_is_untaxed():
    r = realized_pnl([_t(100, 150, days=400)], COSTS)  # held > 12 months
    assert r.short_term_gain == 0.0 and r.stcg == 0.0
    assert r.net == 500.0 - 40.0 - 2.5 - 0.75


def test_short_term_loss_offsets_gain():
    # +500 ST gain and -300 ST loss → STCG on the net +200 only
    r = realized_pnl([_t(100, 150), _t(100, 70)], COSTS)
    assert r.short_term_gain == 200.0
    assert r.stcg == 40.0  # 20% * 200


def test_net_short_term_loss_has_no_tax():
    r = realized_pnl([_t(100, 110), _t(100, 50)], COSTS)  # +100 and -500 → net -400
    assert r.short_term_gain == -400.0 and r.stcg == 0.0


def test_empty_is_zero():
    r = realized_pnl([], COSTS, target=1000)
    assert r.gross == 0.0 and r.net == 0.0 and r.trades == 0 and r.vs_target == -1000.0


def test_costs_are_config_driven():
    free = CostsCfg(brokerage_per_order_inr=0, stt_pct=0, friction_pct=0, stcg_pct=0)
    r = realized_pnl([_t(100, 150)], free)
    assert r.net == 500.0  # zeroed knobs → gross == net
