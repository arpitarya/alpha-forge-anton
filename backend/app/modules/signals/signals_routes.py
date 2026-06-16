"""Signals endpoints — the deterministic review + the active strategy config.

`GET /signals/review` returns an `ActionPlan` over current holdings (no LLM in the
numbers); `GET /signals/screen` ranks buy-candidates from the configured universe;
`GET /signals/strategy` returns the active typed config so the UI (and Orff, later)
can show and discuss the knobs. All are auth-gated like the rest of the API.
`generated_at` is added here, never inside the plan, to keep the plan itself
byte-identical for the determinism contract.
"""

from __future__ import annotations

from datetime import UTC, datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from app.core.deps import get_current_user
from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.signals import objective_tuning, plan_store, strategy_tuning
from app.modules.signals.objective_config import load_objective
from app.modules.signals.objective_tuning import ObjectiveUpdate
from app.modules.signals.pnl_tracker import monthly_target, realized_pnl
from app.modules.signals.review_service import build_action_plan, build_review
from app.modules.signals.screen_service import build_screen
from app.modules.signals.signal_schema import PnlRequest, RealizedTrade, StrategyChange
from app.modules.signals.strategy_config import load_config
from app.modules.signals.weekly_service import weekly_review

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/review")
async def get_review() -> dict:
    plan, diff = await build_review()
    return {
        **plan.model_dump(),
        "diff": diff.model_dump(),
        "generated_at": datetime.now(UTC).isoformat(),
    }


@router.post("/plan")
async def save_plan() -> dict:
    """Persist the current ActionPlan to the elgar `actions/` ledger (the Save button)."""
    holdings = HoldingsAggregator().all_holdings()
    plan = await build_action_plan(holdings=holdings)
    saved = plan_store.to_saved(plan, holdings, plan_store.new_plan_id())
    ref = await plan_store.save(saved)
    return {"ref": ref, "plan_id": saved.plan_id}


@router.get("/screen")
async def get_screen(theme: str | None = None, limit: int | None = None) -> dict:
    result = await build_screen(theme=theme, limit=limit)
    return {**result.model_dump(), "generated_at": datetime.now(UTC).isoformat()}


@router.get("/weekly")
async def get_weekly() -> dict:
    """The weekly review job Cowork's scheduler triggers — actions + fired stops."""
    review = await weekly_review()
    return {**review.model_dump(), "generated_at": datetime.now(UTC).isoformat()}


@router.get("/objective")
async def get_objective() -> dict:
    obj = load_objective()
    return obj.model_dump() | {"active_target": obj.active_target(), "generated_at": datetime.now(UTC).isoformat()}


@router.post("/objective")
async def set_objective(body: ObjectiveUpdate) -> dict:
    try:
        obj = await objective_tuning.apply(body.model_dump(exclude_none=True))
    except (ValueError, ValidationError) as e:
        raise HTTPException(422, f"invalid objective: {e}") from e
    return obj.model_dump() | {"active_target": obj.active_target()}


@router.post("/pnl")
async def get_pnl(body: PnlRequest) -> dict:
    """Monthly realized P&L, net of brokerage + STT + friction + STCG vs target."""
    target = body.target or monthly_target()
    report = realized_pnl(body.trades, load_config().costs, target)
    return report.model_dump()


@router.get("/strategy")
async def get_strategy() -> dict:
    return load_config().model_dump()


@router.post("/strategy")
async def set_strategy(body: StrategyChange) -> dict:
    """Apply a confirmed strategy-knob change (the ApprovalCard's Approve target)."""
    try:
        cfg = await strategy_tuning.apply(body.knob, body.value)
    except (KeyError, ValueError, ValidationError) as e:
        raise HTTPException(422, f"invalid strategy change: {e}") from e
    return cfg.model_dump()
