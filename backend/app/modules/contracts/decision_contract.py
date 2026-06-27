"""A decision-journal row — the audit trail of approve/veto and how it resolved.

Pairs the proposal the human saw (including the downside that was shown — `downside_shown`,
proving the cone led) with the decision and its eventual outcome. `replayable` asserts the
inputs were captured well enough to re-run the decision deterministically — the integrity
property the journal exists to guarantee.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.contracts.approval_contract import ApprovalProposal

Decision = Literal["approved", "vetoed"]
Outcome = Literal["cleared_cone", "hit_stop", "open"]


class DecisionRow(BaseModel):
    """One row of the decision journal — what was proposed, decided, and what happened."""

    date: date
    proposal: ApprovalProposal = Field(default_factory=ApprovalProposal)
    downside_shown: float = 0.0  # the expected-shortfall the human actually saw
    decision: Decision = "vetoed"
    outcome: Outcome = "open"
    replayable: bool = False
