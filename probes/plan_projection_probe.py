"""Projection + save-plan probe — the Fux-assumptions math and the elgar write path.

1. Projection: compound math against a closed form, plan-mix rate consistency
   with the committed `capital-market-assumptions` entry × plan targets.
2. Save plan: `elgar_bridge.save` round-trip into a throwaway store
   (`ELGAR_DIR=<tmp>`), asserting the doc lands and is git-committed there —
   personal figures never touch this repo.

Standalone — no backend server, no CDP. Run:  just probe plan-projection
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def probe_projection() -> None:
    from app.modules.plans import projection_service as ps

    a = ps.assumptions()
    check("assumptions cover every plan class",
          set(a["expected_return_pa"]) >= {"equity", "bond", "gold", "cash"})
    p = ps.project(100_000, 0, 10, "gold")
    closed = 100_000 * (1 + a["expected_return_pa"]["gold"] / 100) ** 10
    check("lump-sum compounding matches closed form", abs(p["nominal"][-1] - closed) < 1)
    check("real < nominal under positive inflation", p["real"][-1] < p["nominal"][-1])
    check("series lengths match years", len(p["nominal"]) == len(p["years"]) == 10)
    mix = ps.rate_for(None)
    check("plan-mix rate within class bounds",
          min(a["expected_return_pa"].values()) <= mix <= max(a["expected_return_pa"].values()),
          str(mix))
    check("response cites the assumptions entry", "capital-market-assumptions" in p["assumptions_ref"])


def probe_save_plan(tmp: str) -> None:
    from app.modules.plans import elgar_bridge

    os.environ["ELGAR_DIR"] = tmp
    subprocess.run([elgar_bridge._bin(), "init"], capture_output=True, check=True)
    ref = asyncio.run(elgar_bridge.save("probe-plan", "---\nid: probe-plan\nstatus: draft\n---\n# t\n₹5,00,000 corpus\n"))
    check("save returns the elgar ref", ref == "elgar://plan/probe-plan")
    doc = Path(tmp) / "plans" / "probe-plan.plan.md"
    check("doc lands in the store", doc.exists())
    log = subprocess.run(["git", "log", "--oneline"], cwd=tmp, capture_output=True, text=True)
    check("save is git-committed in the store", "probe-plan" in log.stdout)
    check("doc never lands in this repo", not (ROOT / "probe-plan.plan.md").exists())


def main() -> int:
    probe_projection()
    with tempfile.TemporaryDirectory() as tmp:
        probe_save_plan(tmp)
    print("\n" + ("❌ projection/save probe FAILED" if _fail else "✅ projections + save-plan hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
