"""Per-branch unit tests for the re-plan diff (handoff §7).

Pure: build a saved-plan snapshot, change today's holdings, and assert each diff
branch — exited / new / stops fired / un-acted verdict — fires independently.

    uv run pytest tests/test_plan_diff.py -v
"""

from __future__ import annotations

from app.modules.brokers.broker_schemas import AssetClass, Holding
from app.modules.signals.plan_diff import diff
from app.modules.signals.signal_schema import Action, HoldingSnap, SavedPlan, Verdict


def _h(symbol: str, qty: float, price: float = 100.0) -> Holding:
    return Holding(
        source="fix",
        asset_class=AssetClass.EQUITY,
        symbol=symbol,
        quantity=qty,
        avg_price=100,
        last_price=price,
        invested=1000,
        current_value=qty * price,
        pnl=0,
        pnl_pct=0,
        currency="INR",
        exchange="NSE",
    )


def _snap(symbol: str, qty: float, price: float = 100.0) -> HoldingSnap:
    return HoldingSnap(symbol=symbol, qty=qty, value=qty * price, price=price)


SAVED = SavedPlan(
    plan_id="plan-1",
    config_hash="x",
    snapshot=[_snap("HAL", 10), _snap("BEL", 5), _snap("OLD", 3), _snap("DROP", 8)],
    verdicts=[
        Verdict(symbol="HAL", action=Action.TRIM, reason="+60%", stop_price=90),
        Verdict(symbol="OLD", action=Action.SELL, reason="stop", stop_price=120),
        Verdict(symbol="DROP", action=Action.HOLD, reason="hold", stop_price=150),
    ],
)
# HAL unchanged (unacted TRIM); DROP price 100 < its 150 stop (fired); NEW added; BEL+OLD gone.
TODAY = [_h("HAL", 10), _h("DROP", 8, price=100.0), _h("NEW", 7)]


def test_exited_and_new():
    d = diff(TODAY, SAVED)
    assert d.exited == ["BEL", "OLD"]
    assert d.new_positions == ["NEW"]


def test_stops_fired():
    assert diff(TODAY, SAVED).stops_fired == ["DROP"]


def test_unacted_verdict():
    # HAL had a TRIM last plan but qty is unchanged → un-acted
    assert diff(TODAY, SAVED).unacted == ["HAL: TRIM last plan, unchanged"]


def test_acted_trim_not_flagged():
    # if HAL's qty changed materially, the TRIM was acted on → not un-acted
    today = [_h("HAL", 4), _h("DROP", 8, price=200.0), _h("NEW", 7)]
    d = diff(today, SAVED)
    assert d.unacted == [] and d.stops_fired == []  # DROP now above its stop too


def test_no_plan_is_empty_diff():
    d = diff(TODAY, None)
    assert d.exited == [] and d.new_positions == [] and d.unacted == []
