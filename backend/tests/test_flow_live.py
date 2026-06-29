"""Live stage — prepare the exact orders + reconcile fills; NEVER place a broker order.

Pins the hard invariant and the math: the order plan is copy-only (entry + staged -12/-20
guard) and its checklist says Orff never places an order; reconciliation computes true P&L,
slippage vs the planned notional, and lights the guard (soft at -12%, hard at -20%); and Live
unlocks only for an APPROVED edge in the derivation.

    uv run pytest tests/test_flow_live.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow import flow_live
from app.modules.flow.flow_live_schema import Fill, GuardState, OrderKind
from app.modules.flow.flow_schema import StageId, StageState
from app.modules.flow.flow_stages import derive


def test_order_plan_is_copy_only_with_staged_guard():
    plan = flow_live.build_plan("edge-x", "buy winners", 62_500.0)
    kinds = [o.kind for o in plan.orders]
    assert kinds == [OrderKind.ENTRY, OrderKind.GUARD, OrderKind.GUARD]
    assert plan.soft_guard_pct == -12.0 and plan.hard_guard_pct == -20.0
    assert any("never places an order" in c for c in plan.checklist)


def test_reconcile_true_pnl_and_slippage():
    # bought ₹1,00,000 (incl. fees) against a ₹62,500 plan → +₹37,500 slippage; now worth ₹90,000
    fills = [Fill(symbol="X", qty=100, buy_price=1000, fees=0, last_price=900)]
    r = flow_live.reconcile(62_500.0, fills)
    assert r.invested == 100_000.0 and r.current_value == 90_000.0
    assert r.pnl == -10_000.0 and r.pnl_pct == -10.0
    assert r.slippage == 37_500.0  # invested - planned notional


def test_guard_lights_at_minus_12_and_minus_20():
    soft = flow_live.reconcile(
        100_000.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=870)]
    )
    assert soft.guard == GuardState.SOFT  # -13%
    hard = flow_live.reconcile(
        100_000.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=790)]
    )
    assert hard.guard == GuardState.HARD  # -21%
    ok = flow_live.reconcile(
        100_000.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=1050)]
    )
    assert ok.guard == GuardState.OK


def test_live_unlocks_only_on_a_pass():
    spec = EdgeSpec(
        id="e",
        hypothesis="h",
        signal="momentum",
        pre_registered_at=datetime(2026, 6, 1, tzinfo=UTC),
    )
    pas = JournalRecord(edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=3, passed=True)
    kill = JournalRecord(edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=0, passed=False)
    assert {s.id: s for s in derive(spec, pas)}[StageId.LIVE].state == StageState.ACTIVE
    assert {s.id: s for s in derive(spec, kill)}[StageId.LIVE].state == StageState.BLOCKED
    assert {s.id: s for s in derive(spec, None)}[StageId.LIVE].state == StageState.NA
