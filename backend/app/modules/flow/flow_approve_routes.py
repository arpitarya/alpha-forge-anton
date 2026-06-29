"""Approve endpoints — the downside-first proposal, and the human's binary decision.

The proposal is assembled deterministically from the run cone + sizing + the red-team critique;
the decision (approve-as-proposed / veto-with-reason) is ack-gated, PII-guarded, journaled to
elgar, and cooldown-spaced. NOTHING here places an order — Live prepares the orders the human
places. Gated: the Approve stage unlocks only for a surviving (passing) edge.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.modules.contracts.approval_contract import ApprovalProposal, Calibration
from app.modules.flow import (
    flow_approve,
    flow_decision_store,
    flow_jobs,
    flow_redteam,
    flow_service,
)
from app.modules.flow.flow_decision_schema import ApproveState, DecisionRecord, DecisionRequest
from app.modules.flow.flow_run_schema import RunPhase
from app.modules.flow.flow_sizing import size
from app.modules.flow.flow_sizing_schema import SizingInputs
from app.modules.plans.elgar_bridge import ElgarStoreError

router = APIRouter()


async def _proposal(edge_id: str) -> tuple[ApprovalProposal, SizingInputs, object]:
    flow = await flow_service.load_flow(edge_id)
    if flow is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    run = flow_jobs.latest_for(edge_id)
    if (
        run is None
        or run.phase != RunPhase.DONE
        or run.report is None
        or run.report.verdict != "pass"
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, "approve unlocks only for a surviving edge")
    inputs = SizingInputs()
    sizing = size(inputs)
    rt = flow_redteam.get(edge_id)
    proposal = flow_approve.proposal_from(
        flow.hypothesis, sizing.recommended_notional, inputs.guard_pct, rt, Calibration()
    )
    return proposal, sizing, rt


def _cooldown_active(latest: DecisionRecord | None) -> bool:
    if latest is None or not latest.cooldown_until:
        return False
    return datetime.fromisoformat(latest.cooldown_until) > datetime.now(UTC)


@router.get("/edges/{edge_id}/approve", response_model=ApproveState)
async def get_approve(edge_id: str) -> ApproveState:
    """The proposal (downside-first), the exec checklist, red-team readiness, the live decision."""
    proposal, sizing, rt = await _proposal(edge_id)
    latest = await flow_decision_store.latest(edge_id)
    return ApproveState(
        proposal=proposal,
        checklist=flow_approve.exec_checklist(proposal, sizing.recommended_pct, sizing.binding),
        redteam_ready=rt is not None and rt.phase == RunPhase.DONE,
        decision=latest,
        can_decide=not _cooldown_active(latest),
    )


@router.post("/edges/{edge_id}/decision", response_model=DecisionRecord, status_code=201)
async def post_decision(edge_id: str, req: DecisionRequest) -> DecisionRecord:
    """Record the human's binary decision — ack-gated, PII-guarded, journaled to elgar (loud)."""
    proposal, _sizing, _rt = await _proposal(edge_id)
    if _cooldown_active(await flow_decision_store.latest(edge_id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "a logged cooldown is still active")
    try:
        return await flow_approve.decide(edge_id, req, proposal)
    except flow_approve.DecisionError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    except ElgarStoreError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
