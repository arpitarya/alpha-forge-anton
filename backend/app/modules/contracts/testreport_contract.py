"""The edge funnel's verdict shape — what gate validation reports to the UI.

**Shapes only — Phase 1 fills the numbers.** This is the funnel-level report (overfitting
probability, deflated Sharpe, the multiple-testing haircut, the walk-forward summary) that
later phases compute by composing the existing `edges` gate results. `pre_registered_at` is
the discipline anchor carried through from the `EdgeSpec`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["pass", "fail"]


class Walkforward(BaseModel):
    """Aggregate walk-forward consistency — the gate-2 summary."""

    agg_calmar: float = 0.0
    pct_windows_positive: float = 0.0  # fraction of test windows net-positive


class TestReport(BaseModel):
    """One edge's validation verdict. Byte-identical for the same edge + bars (no clock)."""

    edge_id: str
    gates_passed: list[int] = Field(default_factory=list)  # gate numbers cleared
    pbo: float = 0.0  # probability of backtest overfitting
    deflated_sharpe: float = 0.0
    haircut_t: float = 0.0  # multiple-testing t-stat haircut
    walkforward: Walkforward = Field(default_factory=Walkforward)
    verdict: Verdict = "fail"
    pre_registered_at: datetime | None = None
