"""The program mandate — the north-star Orff optimises every decision toward.

Distinct from `signals.objective_config.Objective` (the monthly ₹ swing target): this is
the *governance* contract — the calmar bar, the drawdown guard rails, the self-funding
ledger, and the locked capital structure. It is **read-only on the live surface and
editable only in Goals**; `capital_structure.reserve` is **LOCKED** (never deployed).
Defaults carry the roadmap-locked values (calmar 3/2, drawdown -12/-20).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Horizon = Literal["swing", "long_term"]
RiskTolerance = Literal["conservative", "moderate", "aggressive"]


class DrawdownGuard(BaseModel):
    """Equity drawdown rails, in percent (negative = a loss)."""

    soft: float = -12.0  # de-risk / pause new deployment
    hard: float = -20.0  # full stop — flatten and review


class SelfFunding(BaseModel):
    """Is the program paying for itself? `covered` is honest-pending (None) until a
    realised-P&L source exists (Gate-4 paper); cage savings reduce opex, not income."""

    opex_per_month: float = 0.0  # INR; gross fixed opex from funding.subscriptions
    cage_savings_per_month: float = 0.0  # tool savings that REDUCE opex — never income
    reserve: float = 0.0  # INR runway held against opex
    covered: bool | None = None  # realised P&L ≥ net opex; None until Gate-4 paper


class CapitalStructure(BaseModel):
    """Deployable capital by venue, in INR. `reserve` is LOCKED — never deployed."""

    groww: float = 0.0
    zerodha: float = 0.0
    reserve: float = 0.0  # LOCKED — editable only in Goals, never auto-deployed


class Objective(BaseModel):
    """The program mandate — read-only on the live surface, editable only in Goals."""

    aim: str = ""
    calmar_target: float = 3.0
    calmar_floor: float = 2.0
    drawdown_guard: DrawdownGuard = Field(default_factory=DrawdownGuard)
    horizon: Horizon = "swing"
    risk_tolerance: RiskTolerance = "aggressive"
    self_funding: SelfFunding = Field(default_factory=SelfFunding)
    capital_structure: CapitalStructure = Field(default_factory=CapitalStructure)
