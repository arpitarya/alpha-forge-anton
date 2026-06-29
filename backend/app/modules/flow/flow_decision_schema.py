"""Approve-stage shapes — the proposal the human sees and the decision they make.

Downside-first and ack-loss-first by construction: the proposal leads with the worst-case
loss (`ApprovalProposal.expected_shortfall`), and a decision to APPROVE is refused unless the
human acknowledged that loss. The decision is the durable artifact — it journals to the
private elgar store (never ₹/money docs to this repo); a free-text veto reason is PII-guarded
before it is written. A logged cooldown spaces decisions so nothing is approved on a hot streak.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.modules.contracts.approval_contract import ApprovalProposal

Decision = Literal["approved", "vetoed"]


class DecisionRequest(BaseModel):
    """The human's call on a proposal — binary, ack-gated, with a reason when vetoing."""

    decision: Decision
    ack_loss: bool = False  # APPROVE requires the worst-case loss was acknowledged first
    veto_reason: str = ""  # VETO requires a reason (PII-guarded before it reaches elgar)


class DecisionRecord(BaseModel):
    """The persisted decision — what was decided, the downside shown, when, and the cooldown."""

    edge_id: str
    decision: Decision
    thesis: str = ""
    notional: float = 0.0  # the approved position size ₹ — Live prepares orders to exactly this
    downside_shown: float = 0.0  # the worst-case ₹ loss the human actually saw + acknowledged
    veto_reason: str = ""
    decided_at: str = ""  # ISO UTC — server-stamped
    cooldown_until: str = ""  # ISO UTC — no re-decision before this
    ref: str | None = None  # elgar://plan/<id> (link only; the doc lives off-repo)


class ApproveState(BaseModel):
    """Everything the Approve panel needs — the proposal, the checklist, and the live decision."""

    proposal: ApprovalProposal = Field(default_factory=ApprovalProposal)
    checklist: list[str] = Field(default_factory=list)  # execution steps shown ON approve
    redteam_ready: bool = False  # has the 10th-Man critique been run (you-say-yes after seeing it)
    decision: DecisionRecord | None = None  # the latest persisted decision, if any
    can_decide: bool = True  # False while a logged cooldown is still active
