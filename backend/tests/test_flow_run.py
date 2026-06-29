"""Flow Test-stage — the async job lifecycle + honest gate derivation (no heavy funnel).

Pins the cheap, deterministic logic: `gates_from_report` maps a completed report to
per-gate progress (Gate-0 passed, the killer gate FAILED, the rest SKIPPED), and the
in-memory job registry runs one job per edge with no double-run. The expensive
determinism check (a UI run equals the CLI run) lives in `flow_run_probe.py --heavy`
and `test_eb0_real.py`; here we mock the run so the suite stays fast.

    uv run pytest tests/test_flow_run.py -v
"""

from __future__ import annotations

import asyncio

import pytest

from app.modules.contracts.cone_contract import Cone
from app.modules.contracts.testreport_contract import TestReport
from app.modules.edges.eb0_cli import edge_001
from app.modules.edges.funnel import FunnelResult
from app.modules.flow import flow_jobs, flow_run
from app.modules.flow.flow_run_schema import GateState, RunPhase


def _report(gates_passed: list[int], verdict: str = "fail") -> TestReport:
    return TestReport(edge_id="edge-x", gates_passed=gates_passed, verdict=verdict)


def test_resolve_spec_edge001_is_the_pinned_cli_spec():
    # the UI run must be byte-identical to the CLI → same spec the CLI runs
    assert asyncio.run(flow_run.resolve_spec("edge-001")).id == edge_001().id


def test_gates_kill_marks_killer_failed_and_rest_skipped():
    gates = {g.gate: g for g in flow_run.gates_from_report(_report([]))}
    assert gates[0].state == GateState.PASSED  # panel is Gate-0 clean
    assert gates[1].state == GateState.FAILED  # the gate that killed it
    assert gates[2].state == GateState.SKIPPED and gates[3].state == GateState.SKIPPED


def test_gates_full_pass_all_passed():
    gates = {g.gate: g for g in flow_run.gates_from_report(_report([1, 2, 3], "pass"))}
    assert all(gates[g].state == GateState.PASSED for g in (0, 1, 2, 3))


def test_gates_mid_kill_at_gate2():
    gates = {g.gate: g for g in flow_run.gates_from_report(_report([1]))}
    assert gates[1].state == GateState.PASSED
    assert gates[2].state == GateState.FAILED
    assert gates[3].state == GateState.SKIPPED


@pytest.mark.asyncio
async def test_job_runs_once_and_records_result(monkeypatch):
    result = FunnelResult(
        report=_report([1, 2, 3], "pass"), cone=Cone(horizon="52w"), signature="abc123", notes=[]
    )

    async def _fake_run(edge_id: str) -> FunnelResult:
        await asyncio.sleep(0)
        return result

    monkeypatch.setattr(flow_run, "run_edge", _fake_run)
    flow_jobs._JOBS.clear()
    flow_jobs._BY_EDGE.clear()

    started = flow_jobs.start("edge-x")
    assert started.phase == RunPhase.QUEUED
    second = flow_jobs.start("edge-x")  # no double-run while in flight
    assert second.job_id == started.job_id

    await asyncio.sleep(0.05)  # let the task finish
    done = flow_jobs.get(started.job_id)
    assert done.phase == RunPhase.DONE
    assert done.report.verdict == "pass" and done.signature == "abc123"
    assert flow_jobs.latest_for("edge-x").job_id == started.job_id
