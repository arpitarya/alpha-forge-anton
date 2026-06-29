"""Approve stage — downside-first proposal + the ack-gated, PII-guarded, journaled decision.

The elgar write is MOCKED (no real store commit). Pins: the proposal leads with the worst-case
₹ loss (notional at the hard guard) and carries the red-team critique; APPROVE is refused without
acknowledging the loss; VETO needs a reason; a PAN/Aadhaar/account in the reason is BLOCKED before
it reaches elgar; a decision server-stamps a cooldown; the exec checklist never places an order.

    uv run pytest tests/test_flow_approve.py -v
"""

from __future__ import annotations

import pytest

from app.modules.contracts.approval_contract import Calibration
from app.modules.flow import flow_approve
from app.modules.flow.flow_decision_schema import DecisionRecord, DecisionRequest
from app.modules.flow.flow_redteam_schema import RedteamObjection, RedteamReport

_RT = RedteamReport(
    objections=[RedteamObjection(severity="high", title="overfit")],
    tenth_man="momentum crashes",
    tripwires=["NIFTY < 200DMA"],
)


def _proposal():
    return flow_approve.proposal_from("buy winners", 62_500.0, 20.0, _RT, Calibration())


def test_proposal_is_downside_first_with_redteam():
    p = _proposal()
    assert p.expected_shortfall == 12_500.0  # 62.5k notional at the -20% guard
    assert p.stress == p.expected_shortfall and p.notional == 62_500.0
    assert p.red_team == ["overfit"] and p.tenth_man == "momentum crashes"


def test_exec_checklist_never_places_an_order():
    steps = flow_approve.exec_checklist(_proposal(), 6.25, "fractional-kelly")
    assert len(steps) == 5
    assert any("never places the order" in s for s in steps)
    assert any("guard" in s for s in steps)  # staged -12 / -20 discipline


@pytest.mark.asyncio
async def test_approve_requires_ack_loss(monkeypatch):
    monkeypatch.setattr(flow_approve.flow_decision_store, "save", _save_spy())
    with pytest.raises(flow_approve.DecisionError, match="acknowledg"):
        await flow_approve.decide(
            "e", DecisionRequest(decision="approved", ack_loss=False), _proposal()
        )


@pytest.mark.asyncio
async def test_veto_requires_reason_and_pii_is_blocked(monkeypatch):
    monkeypatch.setattr(flow_approve.flow_decision_store, "save", _save_spy())
    with pytest.raises(flow_approve.DecisionError, match="reason"):
        await flow_approve.decide(
            "e", DecisionRequest(decision="vetoed", veto_reason="  "), _proposal()
        )
    with pytest.raises(flow_approve.DecisionError, match="hard identifier"):
        await flow_approve.decide(
            "e", DecisionRequest(decision="vetoed", veto_reason="see PAN ABCDE1234F"), _proposal()
        )


@pytest.mark.asyncio
async def test_clean_decision_persists_and_stamps_cooldown(monkeypatch):
    saved: dict[str, DecisionRecord] = {}

    async def _save(rec: DecisionRecord) -> str:
        saved["rec"] = rec
        return f"elgar://plan/{rec.edge_id}"

    monkeypatch.setattr(flow_approve.flow_decision_store, "save", _save)
    rec = await flow_approve.decide(
        "edge-x", DecisionRequest(decision="approved", ack_loss=True), _proposal()
    )
    assert rec.decision == "approved" and rec.downside_shown == 12_500.0
    assert rec.decided_at and rec.cooldown_until > rec.decided_at  # cooldown is in the future
    assert rec.ref == "elgar://plan/edge-x" and saved["rec"].veto_reason == ""


def _save_spy():
    async def _save(rec: DecisionRecord) -> str:  # should never be reached on a refused decision
        raise AssertionError("save must not run when the decision is refused")

    return _save
