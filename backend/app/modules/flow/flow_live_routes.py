"""Live endpoints — the exact orders for an APPROVED edge, and fill reconciliation.

Gated: the order plan is served only for an edge whose latest decision is APPROVED. The
plan is copy-only and the reconciliation reads back human-entered fills — there is NO broker
order-placement call anywhere on this path, and nothing auto-executes (the hard invariant).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.flow import flow_decision_store, flow_live, flow_service
from app.modules.flow.flow_live_schema import Fill, OrderPlan, ReconcileResult

router = APIRouter()


async def _approved_decision(edge_id: str):
    if await flow_service.load_flow(edge_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    decision = await flow_decision_store.latest(edge_id)
    if decision is None or decision.decision != "approved":
        raise HTTPException(status.HTTP_409_CONFLICT, "approve the edge before preparing orders")
    return decision


@router.get("/edges/{edge_id}/live", response_model=OrderPlan)
async def get_order_plan(edge_id: str) -> OrderPlan:
    """The exact orders + checklist + staged guard for an approved edge. Copy-only, human-placed."""
    d = await _approved_decision(edge_id)
    return flow_live.build_plan(edge_id, d.thesis, d.notional)


@router.post("/edges/{edge_id}/reconcile", response_model=ReconcileResult)
async def post_reconcile(edge_id: str, fills: list[Fill]) -> ReconcileResult:
    """True-P&L read-back from the human's actual fills vs the approved plan. No broker call."""
    d = await _approved_decision(edge_id)
    return flow_live.reconcile(d.notional, fills)
