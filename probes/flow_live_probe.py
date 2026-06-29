"""Flow Live probe — prepare orders + reconcile fills; the NEVER-auto-execute invariant (no CDP).

Asserts: the order plan is copy-only (entry + the staged -12/-20 guard) and its checklist says
Orff never places an order; reconciliation computes true P&L + slippage vs the planned notional;
the guard lights soft at -12% and hard at -20%; and the live module contains NO broker
order-placement call (no kite/groww/order/place_order). Deterministic, no broker dependency.

Run:  just probe flow-live
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'OK' if ok else 'XX'} {name}{('  -- ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    from app.modules.flow import flow_live
    from app.modules.flow.flow_live_schema import Fill, GuardState, OrderKind

    plan = flow_live.build_plan("edge-x", "buy winners", 62_500.0)
    kinds = [o.kind for o in plan.orders]
    check("plan is entry + 2 staged guards", kinds == [OrderKind.ENTRY, OrderKind.GUARD, OrderKind.GUARD])
    check("staged guard is -12 / -20", plan.soft_guard_pct == -12.0 and plan.hard_guard_pct == -20.0)
    check("checklist says Orff never places an order",
          any("never places an order" in c for c in plan.checklist))

    r = flow_live.reconcile(62_500.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=900)])
    check("true P&L computed", r.invested == 100_000.0 and r.pnl == -10_000.0 and r.pnl_pct == -10.0)
    check("slippage vs plan", r.slippage == 37_500.0)
    soft = flow_live.reconcile(100_000.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=870)])
    hard = flow_live.reconcile(100_000.0, [Fill(symbol="X", qty=100, buy_price=1000, last_price=790)])
    check("guard lights soft at -12% and hard at -20%",
          soft.guard == GuardState.SOFT and hard.guard == GuardState.HARD)

    # the hard invariant: the Live engine imports no broker module and calls no placement API
    files = [Path(flow_live.__file__), Path(flow_live.__file__.replace(".py", "_routes.py"))]
    imports = [ln for f in files for ln in f.read_text().splitlines() if ln.startswith(("import ", "from "))]
    check("Live imports no broker module", "broker" not in "\n".join(imports).lower())
    body = " ".join(f.read_text() for f in files).lower()
    placement = ("place_order", "order_place", "submit_order", "kite_connect", ".place(", "groww_api")
    check("no broker order-placement call in the Live engine",
          not any(b in body for b in placement), next((b for b in placement if b in body), ""))

    print("\n" + ("XX flow-live probe FAILED" if _fail else "OK Live (prepare + reconcile) guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
