"""Plan endpoints — the active rebalance plan and live drift against it.

Serves the **plan store** (elgar, via `plan_loader`) joined with live actuals
(`plan_drift`). Drift is returned in percentage points only — no ₹, no symbols —
matching the two-plane rule in the Fux `secure-holdings-plan` entry. This is the REST
sibling of the concierge's `disclosed_context`: both read `plan_drift`, one source two
consumers (cf. the registry single-source pattern).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.plans import elgar_bridge, projection_service
from app.modules.plans.plan_drift import drift_for_plan, has_live_data
from app.modules.plans.plan_loader import available_plans, load_plan
from app.modules.plans.plans_schemas import PlanSaveRequest, PlanSaveResponse, frontmatter

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("")
async def get_plan(plan_id: str = "core-allocation"):
    """The stored plan: targets, bands, rules, and the list of available plans."""
    try:
        plan = load_plan(plan_id)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    return {
        "plan_id": plan.plan_id,
        "horizon": plan.horizon,
        "targets": {k.value: v for k, v in plan.targets.items()},
        "bands": plan.bands,
        "rules": plan.rules,
        "available": await available_plans(),
    }


@router.get("/drift")
async def get_plan_drift(plan_id: str = "core-allocation"):
    """Band-aware drift vs the plan + the actions to take — percentages only."""
    try:
        plan, rows = drift_for_plan(plan_id)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    return {
        "plan_id": plan.plan_id,
        "live": has_live_data(rows),
        "drift": [r.__dict__ for r in rows],
        "actions": [r.action for r in rows if r.action],
    }


@router.get("/projection")
async def get_projection(years: int = 10, monthly: float = 0.0, initial: float | None = None,
                         asset_class: str | None = None, plan_id: str = "core-allocation"):
    """Forward projection on the committed capital-market assumptions (`fux why
    capital-market-assumptions`). `initial` defaults to the live portfolio value —
    personal figures stay request-scoped, never persisted."""
    if initial is None:
        initial = HoldingsAggregator().totals().get("current_value", 0.0)
    try:
        return projection_service.project(initial, monthly, min(max(years, 1), 50),
                                          asset_class, plan_id)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e


@router.post("", response_model=PlanSaveResponse)
async def save_plan(body: PlanSaveRequest):
    """Save a plan document into the private elgar store (the Orff “Save plan”
    button). Content may carry personal figures — that is the point of the store;
    it never enters this repo (`plan-store`)."""
    plan_id = body.plan_id or elgar_bridge.slugify(body.title)
    doc = body.content if body.content.startswith("---") \
        else frontmatter(plan_id, body.title) + body.content
    try:
        ref = await elgar_bridge.save(plan_id, doc, message=f"orff: save {plan_id}")
    except (RuntimeError, FileNotFoundError) as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e
    return PlanSaveResponse(ref=ref, plan_id=plan_id)
