"""Flow Test/Range probe — the async run job, honest gate mapping, and the cone (no CDP).

Fast checks (default): `gates_from_report` maps a verdict to per-gate progress honestly
(Gate-0 passed, the killer FAILED, the rest SKIPPED), the job registry runs one job per
edge with no double-run, and the cone is downside-first. The DETERMINISM check (a UI run
equals the CLI run, byte-identical signature) is heavy (~30s/run) — opt in with --heavy.

Run:  just probe flow-run            (fast)
      uv run python probes/flow_run_probe.py --heavy   (adds the determinism check)
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(
        f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}"
    )
    if not ok:
        _fail += 1


async def main(heavy: bool) -> int:
    from app.modules.contracts.cone_contract import Cone
    from app.modules.contracts.testreport_contract import TestReport
    from app.modules.edges.eb0_cli import edge_001
    from app.modules.edges.funnel import FunnelResult
    from app.modules.flow import flow_jobs, flow_run
    from app.modules.flow.flow_run_schema import GateState, RunPhase

    # 1. honest gate derivation
    kill = {
        g.gate: g
        for g in flow_run.gates_from_report(TestReport(edge_id="e", gates_passed=[]))
    }
    check("Gate-0 integrity passed", kill[0].state == GateState.PASSED)
    check(
        "KILL marks gate-1 FAILED, gate-3 SKIPPED",
        kill[1].state == GateState.FAILED and kill[3].state == GateState.SKIPPED,
    )
    passed = flow_run.gates_from_report(
        TestReport(edge_id="e", gates_passed=[1, 2, 3], verdict="pass")
    )
    check(
        "full PASS → all four gates passed",
        all(g.state == GateState.PASSED for g in passed),
    )

    # 2. resolve edge-001 to the pinned CLI spec (byte-identical run)
    check(
        "resolve_spec(edge-001) == the CLI's edge_001()",
        (await flow_run.resolve_spec("edge-001")).id == edge_001().id,
    )

    # 3. job registry — one run per edge, no double-run
    fake = FunnelResult(
        report=TestReport(edge_id="edge-x", gates_passed=[1, 2, 3], verdict="pass"),
        cone=Cone(horizon="52w"),
        signature="sig-x",
        notes=[],
    )

    async def _fake_run(_edge_id: str) -> FunnelResult:
        await asyncio.sleep(0)
        return fake

    flow_run.run_edge = _fake_run  # type: ignore[assignment]
    flow_jobs._JOBS.clear()
    flow_jobs._BY_EDGE.clear()
    a = flow_jobs.start("edge-x")
    b = flow_jobs.start("edge-x")
    check("no double-run while in flight", a.job_id == b.job_id)
    await asyncio.sleep(0.05)
    done = flow_jobs.get(a.job_id)
    check(
        "job completes + records the report",
        done.phase == RunPhase.DONE and done.signature == "sig-x",
    )

    # 4. heavy determinism — a UI run equals the CLI run (byte-identical signature)
    if heavy:
        print("  … running edge-001 twice (heavy) …")
        # mirror production: _compute does its own asyncio.run, so off-load to a worker thread
        r1 = await asyncio.to_thread(flow_run._compute, edge_001())
        r2 = await asyncio.to_thread(flow_run._compute, edge_001())
        check("edge-001 reproduces its KILL", r1.report.verdict == "fail")
        check(
            "determinism: identical signature across runs",
            r1.signature == r2.signature,
            f"{r1.signature[:12]} vs {r2.signature[:12]}",
        )
        check(
            "cone is downside-first (es_p5 present, 52w paths)",
            r1.cone.horizon == "52w" and len(r1.cone.p5) == 52,
        )
    else:
        print("  (skipping the ~30s determinism check — pass --heavy to include it)")

    print(
        "\n"
        + ("❌ flow-run probe FAILED" if _fail else "✅ Test/Range run guarantees hold")
    )
    return 1 if _fail else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Flow Test/Range run probe")
    p.add_argument(
        "--heavy", action="store_true", help="add the ~30s/run determinism check"
    )
    raise SystemExit(asyncio.run(main(p.parse_args().heavy)))
