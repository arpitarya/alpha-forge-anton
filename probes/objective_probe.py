"""Objective-config probe — asserts Objective model, step_up resolution, progress_pct maths.

Standalone (no CDP, no elgar). Run:  just probe objective
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "probes"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    from app.modules.signals.objective_config import Objective, StepUp
    from app.modules.signals.objective_loader import _objective_paths
    from app.modules.signals.pnl_tracker import realized_pnl
    from app.modules.signals.signal_schema import RealizedTrade
    from app.modules.signals.strategy_config import CostsCfg

    # 1. Defaults — no file → all zeros, context_text returns ""
    obj = Objective()
    check("defaults: monthly_target_inr == 0", obj.monthly_target_inr == 0.0)
    check("defaults: step_up is None", obj.step_up is None)
    check("defaults: active_target() == 0.0", obj.active_target() == 0.0)
    check("defaults: context_text() is empty", obj.context_text() == "")

    # 2. step_up in the future → active_target returns current monthly_target_inr
    today = date(2026, 6, 15)
    obj_step = Objective(
        monthly_target_inr=2000.0,
        step_up=StepUp(from_date=date(2026, 7, 1), monthly_target_inr=12000.0),
    )
    got = obj_step.active_target(today=today)
    check("future step_up → returns current target (2000)", got == 2000.0, f"got {got}")

    # 3. step_up in the past → returns stepped target
    got = obj_step.active_target(today=date(2026, 8, 1))
    check("past step_up → returns stepped target (12000)", got == 12000.0, f"got {got}")

    # 4. step_up exact from_date → activates (>= semantics)
    got = obj_step.active_target(today=date(2026, 7, 1))
    check("step_up exact from_date → activates", got == 12000.0, f"got {got}")

    # 5. context_text() is non-empty when mission or target is set; empty when both zero
    check("context_text non-empty with mission", bool(Objective(mission="fund the plan").context_text()))
    check("context_text non-empty with target", bool(Objective(monthly_target_inr=2000.0).context_text()))
    check("context_text empty when both zero/empty", Objective().context_text() == "")

    # 6. progress_pct maths — canonical unit test (zero-cost fixture to isolate the formula)
    costs = CostsCfg(brokerage_per_order_inr=0, stt_pct=0, friction_pct=0, stcg_pct=0)
    trade = RealizedTrade(
        symbol="TEST", qty=10, buy_price=100.0, sell_price=120.0,
        buy_date=date(2026, 6, 1), sell_date=date(2026, 6, 14),
    )
    report = realized_pnl([trade], costs, target=2000.0)
    check("net P&L = 200 (10 × 20, no costs)", report.net == 200.0, f"net={report.net}")
    check("vs_target = -1800 (200 − 2000)", report.vs_target == -1800.0, f"vs_target={report.vs_target}")
    check("progress_pct = 10.0 (200/2000×100)", report.progress_pct == 10.0, f"got {report.progress_pct}")

    # 7. target == 0 → progress_pct == 0.0 (no ZeroDivisionError)
    zero_report = realized_pnl([trade], costs, target=0.0)
    check("target=0 → progress_pct=0.0 (no division)", zero_report.progress_pct == 0.0)

    # 8. losing month → progress_pct is negative (raw, not clamped)
    losing = RealizedTrade(
        symbol="TEST", qty=10, buy_price=120.0, sell_price=100.0,
        buy_date=date(2026, 6, 1), sell_date=date(2026, 6, 14),
    )
    losing_report = realized_pnl([losing], costs, target=2000.0)
    check("losing month → progress_pct < 0 (raw, not clamped)",
          losing_report.progress_pct < 0.0, f"got {losing_report.progress_pct}")

    # 9. objective.md seed is figure-free (dante-pii style check)
    seed_path = _objective_paths()[1]
    if seed_path.exists():
        from context_drift_probe import scan_position_figures
        leaks = scan_position_figures(seed_path.read_text())
        check("objective.md seed is figure-free", not leaks, f"leaked: {leaks[:3]}")
    else:
        print(f"⚠  seed {seed_path} not found — skipping figure check")

    print("\n" + ("❌ objective probe FAILED" if _fail else "✅ Objective model + progress_pct guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
