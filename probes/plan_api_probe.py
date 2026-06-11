"""Plan API probe — verifies the /portfolio/plan surface and its leak-safety.

Standalone (no CDP, no HTTP): imports the route handlers and runs them directly, so
it exercises the real serialization path. Asserts the plan reads back consistently and
that the drift payload is percentages-only — no ₹, no symbols — per the Fux
`secure-holdings-plan` two-plane rule.

Run:  just probe plan-api
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "probes"))

from plan_safety_probe import scan_text  # reuse the data-plane leak patterns

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


async def _run() -> None:
    from app.modules.portfolio.plan_routes import get_plan, get_plan_drift

    plan = await get_plan()
    check("plan reads back", plan["plan_id"] == "core-allocation")
    check("targets sum to 100", round(sum(plan["targets"].values()), 2) == 100.0,
          str(plan["targets"]))
    check("core-allocation is listed available", "core-allocation" in plan["available"])

    drift = await get_plan_drift()
    check("drift has a row per plan class", len(drift["drift"]) == len(plan["targets"]))
    payload = json.dumps(drift)
    check("drift payload is percentages-only (no ₹/symbols)", not scan_text(payload),
          f"leaked {scan_text(payload)}")

    # a missing plan 404s cleanly rather than leaking a stack
    from fastapi import HTTPException
    try:
        await get_plan_drift("does-not-exist")
        check("unknown plan rejected", False, "no error raised")
    except HTTPException as e:
        check("unknown plan → 404", e.status_code == 404)


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ plan API probe FAILED" if _fail else "✅ plan API surface holds"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
