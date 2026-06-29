"""Plan-stage sizing — deterministic, four constraints, the binding (smallest) wins.

Pins the sizing math: each constraint's formula, that the recommendation is the minimum
(most conservative) bound clamped to [0, capital], that a 0-ADV input drops the liquidity
cap, and that the same inputs give the same plan (determinism). Also that Plan unlocks
ONLY for a surviving edge (ACTIVE on pass, BLOCKED on kill, NA otherwise).

    uv run pytest tests/test_flow_sizing.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow.flow_schema import StageId, StageState
from app.modules.flow.flow_sizing import size
from app.modules.flow.flow_sizing_schema import SizingInputs
from app.modules.flow.flow_stages import derive

_SPEC = EdgeSpec(
    id="e", hypothesis="h", signal="momentum", pre_registered_at=datetime(2026, 6, 1, tzinfo=UTC)
)


def test_each_constraint_formula():
    r = size(SizingInputs(capital=1_000_000, adv_inr=5_000_000, win_prob=0.55))
    by = {c.name: c.notional for c in r.constraints}
    assert by["fixed-risk"] == 125_000.0  # 1% / 8%
    assert by["downside-cap"] == 600_000.0  # 12% / 20%
    assert by["adv-cap"] == 500_000.0  # 10% of 50L
    assert round(by["fractional-kelly"]) == 62_500  # 0.25 * (0.55 - 0.45/1.5) * 10L


def test_binding_is_the_minimum_and_clamped():
    r = size(SizingInputs(capital=1_000_000, adv_inr=5_000_000, win_prob=0.55))
    assert r.binding == "fractional-kelly"  # the smallest bound
    assert r.recommended_notional == 62_500.0
    assert r.recommended_pct == 6.25
    assert 0 <= r.recommended_notional <= 1_000_000  # clamped to [0, capital]


def test_zero_adv_drops_the_liquidity_cap():
    r = size(SizingInputs(capital=1_000_000))
    assert "adv-cap" not in {c.name for c in r.constraints}  # not shown when ADV missing


def test_sizing_is_deterministic():
    i = SizingInputs(capital=2_000_000, adv_inr=9_000_000)
    assert size(i) == size(i)


def test_plan_unlocks_only_for_a_surviving_edge():
    rec = lambda passed: JournalRecord(  # noqa: E731
        edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=3, passed=passed
    )
    plan = lambda r: {s.id: s for s in derive(_SPEC, r)}[StageId.PLAN].state  # noqa: E731
    assert plan(rec(True)) == StageState.ACTIVE  # passing → sizing available
    assert plan(rec(False)) == StageState.BLOCKED  # killed → no position to size
    assert plan(None) == StageState.NA  # un-run → unlocks after Test
