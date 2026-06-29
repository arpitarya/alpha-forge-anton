"""Flow Plan-stage probe — deterministic position sizing (no CDP, no LLM, no I/O).

Asserts the sizing engine's guarantees: each constraint's formula, that the binding
(smallest) bound is the recommendation clamped to [0, capital], that a 0-ADV input drops
the liquidity cap, that sizing is deterministic, and that Plan unlocks ONLY for a
surviving edge (ACTIVE on pass, BLOCKED on kill). Sizing is SHOWN, never auto-applied.

Run:  just probe flow-sizing
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    from app.modules.edges.edge_journal import JournalRecord
    from app.modules.edges.edge_schema import EdgeSpec
    from app.modules.flow.flow_schema import StageId, StageState
    from app.modules.flow.flow_sizing import size
    from app.modules.flow.flow_sizing_schema import SizingInputs
    from app.modules.flow.flow_stages import derive

    r = size(SizingInputs(capital=1_000_000, adv_inr=5_000_000, win_prob=0.55))
    by = {c.name: c.notional for c in r.constraints}
    check("fixed-risk = 1%/8% = ₹1.25L", by["fixed-risk"] == 125_000.0)
    check("downside-cap = 12%/20% = ₹6L", by["downside-cap"] == 600_000.0)
    check("adv-cap = 10% of ₹50L = ₹5L", by["adv-cap"] == 500_000.0)
    check("fractional-kelly ≈ ₹62.5k", round(by["fractional-kelly"]) == 62_500)
    check("binding = the smallest (fractional-kelly)", r.binding == "fractional-kelly")
    check("recommended = binding, % computed", r.recommended_notional == 62_500.0 and r.recommended_pct == 6.25)
    check("recommended clamped to [0, capital]", 0 <= r.recommended_notional <= 1_000_000)

    no_adv = size(SizingInputs(capital=1_000_000))
    check("0 ADV drops the liquidity cap", "adv-cap" not in {c.name for c in no_adv.constraints})

    i = SizingInputs(capital=2_000_000, adv_inr=9_000_000)
    check("sizing is deterministic", size(i) == size(i))

    spec = EdgeSpec(id="e", hypothesis="h", signal="momentum",
                    pre_registered_at=datetime(2026, 6, 1, tzinfo=UTC))

    def plan_state(passed: bool | None):
        rec = None if passed is None else JournalRecord(
            edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=3, passed=passed)
        return {s.id: s for s in derive(spec, rec)}[StageId.PLAN].state

    check("Plan ACTIVE for a surviving edge", plan_state(True) == StageState.ACTIVE)
    check("Plan BLOCKED for a killed edge", plan_state(False) == StageState.BLOCKED)
    check("Plan NA for an un-run edge", plan_state(None) == StageState.NA)

    print("\n" + ("❌ flow-sizing probe FAILED" if _fail else "✅ Plan sizing guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
