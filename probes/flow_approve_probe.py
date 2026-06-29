"""Flow Approve probe — downside-first proposal + the ack-gated, PII-guarded decision (no CDP).

The elgar write is MOCKED (no real commit). Asserts: the proposal leads with the worst-case ₹
loss and carries the red-team critique; the exec checklist NEVER places an order; APPROVE is
refused without acknowledging the loss; VETO needs a reason; a PAN in the reason is BLOCKED
before it reaches elgar (the same deterministic guard as `append_memory`); a clean decision
server-stamps a cooldown. NOTHING here places a broker order.

Run:  just probe flow-approve
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


async def main() -> int:
    from app.modules.contracts.approval_contract import Calibration
    from app.modules.flow import flow_approve
    from app.modules.flow.flow_decision_schema import DecisionRecord, DecisionRequest
    from app.modules.flow.flow_redteam_schema import RedteamObjection, RedteamReport

    rt = RedteamReport(objections=[RedteamObjection(severity="high", title="overfit")],
                       tenth_man="momentum crashes", tripwires=["NIFTY < 200DMA"])
    p = flow_approve.proposal_from("buy winners", 62_500.0, 20.0, rt, Calibration())
    check("proposal leads with the worst-case loss (notional x guard)", p.expected_shortfall == 12_500.0)
    check("proposal carries the red-team critique", p.red_team == ["overfit"] and p.tenth_man)

    steps = flow_approve.exec_checklist(p, 6.25, "fractional-kelly")
    check("exec checklist never places an order", any("never places the order" in s for s in steps))

    async def _save(rec: DecisionRecord) -> str:
        return f"elgar://plan/{rec.edge_id}"

    flow_approve.flow_decision_store.save = _save  # type: ignore[assignment]

    async def _expect_error(req: DecisionRequest, needle: str) -> bool:
        try:
            await flow_approve.decide("e", req, p)
            return False
        except flow_approve.DecisionError as e:
            return needle in str(e)

    check("APPROVE refused without ack-loss",
          await _expect_error(DecisionRequest(decision="approved", ack_loss=False), "acknowledg"))
    check("VETO refused without a reason",
          await _expect_error(DecisionRequest(decision="vetoed", veto_reason=" "), "reason"))
    check("PAN in the veto reason is BLOCKED before elgar",
          await _expect_error(DecisionRequest(decision="vetoed", veto_reason="PAN ABCDE1234F"), "hard identifier"))

    rec = await flow_approve.decide("edge-x", DecisionRequest(decision="approved", ack_loss=True), p)
    check("clean approve persists + stamps a cooldown",
          rec.decision == "approved" and rec.cooldown_until > rec.decided_at and rec.ref)

    print("\n" + ("❌ flow-approve probe FAILED" if _fail else "✅ Approve (decision) guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
