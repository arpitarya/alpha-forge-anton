"""Plan endpoints — the active rebalance plan and live drift against it.

Serves the committed **plan plane** (`plan_loader`) joined with live actuals
(`plan_drift`). Drift is returned in percentage points only — no ₹, no symbols —
matching the two-plane rule in the Fux `secure-holdings-plan` entry. This is the REST
sibling of the concierge's `disclosed_context`: both read `plan_drift`, one source two
consumers (cf. the registry single-source pattern).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.modules.brokers.plan_drift import drift_for_plan, has_live_data
from app.modules.brokers.plan_loader import available_plans, load_plan

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("")
async def get_plan(plan_id: str = "core-allocation"):
    """The committed plan: targets, bands, rules, and the list of available plans."""
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
        "available": available_plans(),
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
