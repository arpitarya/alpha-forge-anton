"""Approve-stage logic — assemble the downside-first proposal and record the human's call.

`proposal_from` builds the `ApprovalProposal` deterministically from the cone + sizing + the
red-team critique (numbers in, never recomputed). `decide` enforces the discipline: APPROVE
needs the worst-case loss acknowledged first; VETO needs a reason; the reason is PII-guarded
(the same deterministic block as `append_memory`) before it journals to elgar. NOTHING here
places an order — it records a decision; the Live stage prepares the orders the human places.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.modules.concierge import critic_guard
from app.modules.contracts.approval_contract import ApprovalProposal, Calibration
from app.modules.flow import flow_decision_store
from app.modules.flow.flow_decision_schema import DecisionRecord, DecisionRequest
from app.modules.flow.flow_redteam_schema import RedteamReport

COOLDOWN_S = 3600  # logged cooldown between decisions on an edge (nothing approved on a hot streak)


class DecisionError(ValueError):
    """A decision violated the ack-loss-first / reason-required discipline."""


def proposal_from(
    thesis: str, notional: float, guard_pct: float, rt: RedteamReport | None, calib: Calibration
) -> ApprovalProposal:
    """Downside-first proposal — the worst-case ₹ loss (notional at the drawdown guard) leads."""
    shortfall = round(notional * guard_pct / 100, 2)  # loss if the position hits the hard guard
    return ApprovalProposal(
        thesis=thesis,
        notional=round(notional, 2),
        expected_shortfall=shortfall,
        median=0.0,
        stress=shortfall,  # median upside honest-pending (no realised-return source)
        red_team=[o.title for o in rt.objections] if rt else [],
        tenth_man=rt.tenth_man if rt else "",
        runner_ups=rt.runner_ups if rt else [],
        tripwires=rt.tripwires if rt else [],
        calibration=calib,
        cooldown_s=COOLDOWN_S,
    )


def exec_checklist(p: ApprovalProposal, recommended_pct: float, binding: str) -> list[str]:
    """The execution steps shown ON approve — discipline, not orders (Live prepares the orders)."""
    worst = f"{p.expected_shortfall:,.0f}"
    return [
        f"Acknowledge the worst case first: Rs {worst} if the -20% guard breaches.",
        f"Size to the binding constraint ({binding}): {recommended_pct:.2f}% of capital - no more.",
        "Place the entry yourself at or under your limit - Orff never places the order.",
        "Set the staged guard immediately: de-risk at -12%, flatten at -20%.",
        "Log the decision; the tripwires above are your pre-committed exits.",
    ]


async def decide(edge_id: str, req: DecisionRequest, proposal: ApprovalProposal) -> DecisionRecord:
    """Validate the discipline, PII-guard a veto reason, then journal the decision to elgar."""
    if req.decision == "approved" and not req.ack_loss:
        raise DecisionError("APPROVE requires acknowledging the worst-case loss first")
    if req.decision == "vetoed" and not req.veto_reason.strip():
        raise DecisionError("VETO requires a reason")
    if (block := critic_guard.pii_block(req.veto_reason)) is not None:
        raise DecisionError(block)  # money/PII never enters the elgar store from free text
    now = datetime.now(UTC)
    rec = DecisionRecord(
        edge_id=edge_id,
        decision=req.decision,
        thesis=proposal.thesis,
        notional=proposal.notional,
        downside_shown=proposal.expected_shortfall,
        veto_reason=req.veto_reason if req.decision == "vetoed" else "",
        decided_at=now.isoformat(),
        cooldown_until=(now + timedelta(seconds=COOLDOWN_S)).isoformat(),
    )
    rec.ref = await flow_decision_store.save(rec)  # fail-loud: a 503 if the store is unreachable
    return rec
