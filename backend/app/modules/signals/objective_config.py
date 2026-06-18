"""Typed north-star objective — the monthly ₹ target Orff optimises toward.

Resolution: elgar `strategy/objective.md` → repo seed `objective.md` → `Objective()`
defaults (no target, horizon=swing). Same loading chain as `strategy_config`/`config_loader`.
Values (the ₹ target) live only in the elgar copy; the repo seed is figure-free.

See `objective_loader` for file-resolution logic (line-budget split).
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel


class StepUp(BaseModel):
    from_date: date
    monthly_target_inr: float


class Objective(BaseModel):
    monthly_target_inr: float = 0.0
    step_up: StepUp | None = None
    horizon: Literal["swing", "long_term"] = "swing"
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "aggressive"
    mission: str = ""

    def active_target(self, today: date | None = None) -> float:
        """Resolve step_up — a future from_date stays dormant; on/after it activates."""
        d = today or date.today()
        if self.step_up and d >= self.step_up.from_date:
            return self.step_up.monthly_target_inr
        return self.monthly_target_inr

    def context_text(self) -> str:
        """System-block for prompt injection; "" when no target and no mission set."""
        tgt = self.active_target()
        if not tgt and not self.mission:
            return ""
        lines = ["## Objective (north-star — optimise every reply toward this)"]
        if self.mission:
            lines.append(f"Mission: {self.mission}")
        lines.append(f"Horizon: {self.horizon}  |  Risk: {self.risk_tolerance}")
        if tgt:
            lines.append(f"Monthly realized-P&L target: {tgt:.0f} INR")
        return "\n".join(lines)


# Loading split to objective_loader for the line budget; re-exported here so
# objective_config stays the single import surface.
from app.modules.signals.objective_loader import _objective_paths, load_objective  # noqa: E402, F401
