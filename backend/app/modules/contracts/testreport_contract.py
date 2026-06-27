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
QualityStatus = Literal["validated", "disabled-pending"]


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
    data_provenance: str = "synthetic-fixture"  # nse-bhavcopy (real) vs the offline fixture
    date_from: str = ""  # ISO start of the panel the verdict was computed on
    date_to: str = ""  # ISO end
    quality_status: QualityStatus = "validated"  # disabled-pending when no point-in-time feed
    quality_pending: int = 0  # sleeve names that could not be quality-screened (honest gap)
    universe_status: str = "full-fixture"  # per-rebalance-liquid on a real turnover panel
    exclusions_count: int = 0  # never-buy names applied (COUNT only — tickers never enter the repo)
    exclusions_source: str = "none"  # provenance label of the off-repo exclusions doc
