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
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.core.deps import get_current_user
from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.signals import plan_store, strategy_tuning
from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.review_service import build_action_plan, build_review
from app.modules.signals.screen_service import build_screen
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import load_config
from app.modules.signals.weekly_service import weekly_review

router = APIRouter(dependencies=[Depends(get_current_user)])


class StrategyChange(BaseModel):
    knob: str  # dotted path, e.g. "trim_rule.mode"
    value: Any


class PnlRequest(BaseModel):
    """Realized round-trips for the month + the target (figures stay request-scoped)."""

    trades: list[RealizedTrade] = Field(default_factory=list)
    target: float = 0.0


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


@router.post("/pnl")
async def get_pnl(body: PnlRequest) -> dict:
    """Monthly realized P&L, net of brokerage + STT + friction + STCG vs target."""
    report = realized_pnl(body.trades, load_config().costs, body.target)
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
