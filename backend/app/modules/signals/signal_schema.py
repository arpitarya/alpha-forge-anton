"""Pydantic shapes for the signals engine — the deterministic verdict + plan.

`ActionPlan` carries no clock and no nondeterministic field on purpose: the same
holdings + same `StrategyConfig` must serialise byte-identically (the Phase 1
determinism contract). The generated-at timestamp is added by the route response,
never inside the plan itself.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Action(StrEnum):
    SELL = "sell"
    TRIM = "trim"
    HOLD = "hold"
    ADD = "add"


class Verdict(BaseModel):
    symbol: str
    action: Action
    reason: str
    stop_price: float | None = None
    target_price: float | None = None
    conviction: int = Field(0, ge=0, le=5)


class ActionPlan(BaseModel):
    verdicts: list[Verdict] = Field(default_factory=list)
    config_hash: str = ""  # anchors the StrategyConfig the plan was computed under
    universe_mode: str = "themes"


class Candidate(BaseModel):
    """A ranked buy-candidate from the screener (entry/stop/target for a new swing)."""

    symbol: str
    score: float
    entry_price: float
    stop_price: float
    target_price: float
    adx: float
    rsi: float
    pos_52w: float
    reason: str


class ScreenResult(BaseModel):
    candidates: list[Candidate] = Field(default_factory=list)
    config_hash: str = ""
    universe_mode: str = "themes"
    universe_size: int = 0


# Plan-loop + realized-P&L shapes live in plan_schema (line budget); re-exported here
# so signal_schema stays the single import surface. Placed after Verdict is defined.
from app.modules.signals.plan_schema import (  # noqa: E402
    HoldingSnap,
    PlanDiff,
    RealizedReport,
    RealizedTrade,
    SavedPlan,
    WeeklyReview,
)

class StrategyChange(BaseModel):
    knob: str  # dotted path, e.g. "trim_rule.mode"
    value: Any


class PnlRequest(BaseModel):
    """Realized round-trips for the month + target (figures stay request-scoped)."""

    trades: list[RealizedTrade] = Field(default_factory=list)
    target: float = 0.0


__all__ = [
    "Action",
    "ActionPlan",
    "Candidate",
    "HoldingSnap",
    "PlanDiff",
    "PnlRequest",
    "RealizedReport",
    "RealizedTrade",
    "SavedPlan",
    "ScreenResult",
    "StrategyChange",
    "Verdict",
    "WeeklyReview",
]
