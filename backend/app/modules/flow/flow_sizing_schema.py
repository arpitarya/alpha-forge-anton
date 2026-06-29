"""Plan-stage shapes — deterministic position sizing, shown but never auto-applied.

Four independent sizing constraints (fixed fractional risk, downside cap, ADV liquidity
cap, fractional-Kelly); the **binding** (smallest) one wins — the most conservative bound
is the recommendation. Pure inputs, no clock, no I/O: the same inputs give the same plan.
Defaults track the program mandate (drawdown soft -12 / hard -20). Worked-example ₹ only;
this is a recommendation surfaced to the human, NEVER an order (`you-say-yes`).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SizingInputs(BaseModel):
    """Everything the deterministic sizer needs — explicit, with mandate-aligned defaults."""

    capital: float = 1_000_000.0  # ₹ sizing base (worked-example default; the human sets theirs)
    risk_pct: float = 1.0  # fixed fractional risk per trade (% of capital lost if stopped)
    stop_pct: float = 8.0  # per-position stop distance (e.g. the 20-day-low stop)
    max_loss_pct: float = (
        12.0  # downside cap — worst-case position loss ≤ this % (mandate soft guard)
    )
    guard_pct: float = 20.0  # catastrophic per-position move the cap defends (mandate hard guard)
    adv_inr: float = 0.0  # average daily traded value (₹) — 0 disables the ADV cap
    participation_pct: float = 10.0  # max share of a day's liquidity
    win_prob: float = 0.5  # Kelly: probability a trade is net-positive (edge hit-rate)
    payoff_ratio: float = 1.5  # Kelly: average win / average loss
    kelly_fraction: float = 0.25  # fraction of full Kelly to actually take (de-risked)


class SizingConstraint(BaseModel):
    """One sizing method's bound — its notional and a one-line rationale."""

    name: str
    notional: float  # ₹ position this constraint permits
    note: str = ""


class SizingResult(BaseModel):
    """The deterministic plan — every constraint, which one binds, and the recommendation."""

    constraints: list[SizingConstraint] = Field(default_factory=list)
    binding: str = ""  # the constraint that produced the smallest (recommended) notional
    recommended_notional: float = 0.0  # ₹ — the binding minimum, clamped to [0, capital]
    recommended_pct: float = 0.0  # recommended_notional as % of capital
    notes: list[str] = Field(default_factory=list)
