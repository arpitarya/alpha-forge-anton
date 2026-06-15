"""Plan-loop + realized-P&L shapes (Phases 3-4), split from `signal_schema` to keep
each file within the line budget. `signal_schema` re-exports these, so it stays the
single schema import surface — import them from there, not directly.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.modules.signals.signal_schema import Verdict


class HoldingSnap(BaseModel):
    """One row of the holdings snapshot a saved plan was based on (INR values)."""

    symbol: str
    qty: float
    value: float
    price: float


class SavedPlan(BaseModel):
    """An ActionPlan persisted to the elgar `actions/` ledger — what was in force."""

    plan_id: str
    config_hash: str = ""
    snapshot: list[HoldingSnap] = Field(default_factory=list)
    verdicts: list[Verdict] = Field(default_factory=list)


class PlanDiff(BaseModel):
    """What changed since the last saved plan (handoff §7)."""

    exited: list[str] = Field(default_factory=list)
    new_positions: list[str] = Field(default_factory=list)
    stops_fired: list[str] = Field(default_factory=list)
    unacted: list[str] = Field(default_factory=list)  # "PARAS: TRIM last plan, unchanged"


class RealizedTrade(BaseModel):
    """One closed round-trip — the input to the monthly net-P&L tracker (§10.4)."""

    symbol: str
    qty: float
    buy_price: float
    sell_price: float
    buy_date: date
    sell_date: date


class RealizedReport(BaseModel):
    """Realized P&L net of explicit frictions + STCG, vs the month's target."""

    gross: float = 0.0
    brokerage: float = 0.0
    stt: float = 0.0
    friction: float = 0.0
    stcg: float = 0.0
    net: float = 0.0
    short_term_gain: float = 0.0
    target: float = 0.0
    vs_target: float = 0.0
    trades: int = 0


class WeeklyReview(BaseModel):
    """The weekly job's emission — actionable verdicts + fired stops (no auto-trading)."""

    actions: list[Verdict] = Field(default_factory=list)
    stops_fired: list[str] = Field(default_factory=list)
    saved_ref: str | None = None
