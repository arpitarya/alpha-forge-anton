"""Live-stage shapes — the EXACT orders the human places, and the fill reconciliation.

The hard invariant: Orff prepares orders and reconciles fills; it NEVER places a broker
order or auto-executes (`you-say-yes` / `start-small`). `OrderPlan` is a copy-only list the
human executes in their broker; `ReconcileResult` reads back the human-entered fills to compute
true P&L + slippage vs the plan, and lights the staged -12 / -20 guard. Deterministic, no broker
order-placement call, no live-auth dependency — fills are entered by the human.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderKind(StrEnum):
    ENTRY = "entry"  # the position to open
    GUARD = "guard"  # a staged drawdown guard (de-risk / flatten) — a level, not a market order


class PreparedOrder(BaseModel):
    """One line the human copies into their broker — Orff never sends it."""

    side: OrderSide
    kind: OrderKind
    label: str
    notional: float = 0.0  # ₹ for an entry; 0 for a guard level
    level_pct: float = 0.0  # for a guard: the drawdown that triggers it (-12 / -20)


class OrderPlan(BaseModel):
    """The exact orders + checklist for an APPROVED edge — copy-only, human-placed."""

    edge_id: str
    thesis: str = ""
    notional: float = 0.0
    orders: list[PreparedOrder] = Field(default_factory=list)
    soft_guard_pct: float = -12.0  # de-risk / pause new deployment
    hard_guard_pct: float = -20.0  # full stop — flatten and review
    checklist: list[str] = Field(default_factory=list)


class Fill(BaseModel):
    """A fill the human ACTUALLY got — entered by hand (no broker call)."""

    symbol: str
    qty: float
    buy_price: float
    fees: float = 0.0
    last_price: float = 0.0  # current/exit price for the true-P&L read-back (0 → use buy_price)


class GuardState(StrEnum):
    OK = "ok"
    SOFT = "soft"  # past -12% — de-risk
    HARD = "hard"  # past -20% — flatten


class ReconcileResult(BaseModel):
    """True P&L read-back from the human's fills, vs the planned notional + the staged guard."""

    invested: float = 0.0  # Σ qty·buy_price + fees
    current_value: float = 0.0  # Σ qty·last_price
    pnl: float = 0.0
    pnl_pct: float = 0.0
    slippage: float = 0.0  # invested - planned notional (over/under-fill vs the plan)
    guard: GuardState = GuardState.OK
    notes: list[str] = Field(default_factory=list)
