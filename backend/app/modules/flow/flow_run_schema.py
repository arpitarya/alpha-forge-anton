"""Test-stage shapes — the async funnel job's status as the cockpit polls it.

The funnel (Gates 1-3) is invoked whole, never rewritten; per-gate `GateProgress`
is derived from the completed `TestReport.gates_passed` (a gate is `passed` when
cleared, `failed` at the one that killed it, `skipped` after). `RunStatus` carries
the deterministic `TestReport` + downside-first `Cone` on completion — same panel +
seed ⇒ identical report (the determinism contract; a UI run equals the CLI run).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.modules.contracts.cone_contract import Cone
from app.modules.contracts.testreport_contract import TestReport


class RunPhase(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class GateState(StrEnum):
    PENDING = "pending"  # not started / running
    PASSED = "passed"
    FAILED = "failed"  # the gate that killed the edge
    SKIPPED = "skipped"  # downstream of a failed gate — never reached


class GateProgress(BaseModel):
    gate: int  # 0 = integrity, 1 = backtest+overfitting, 2 = walk-forward, 3 = cone
    label: str
    state: GateState = GateState.PENDING


class RunStatus(BaseModel):
    """One funnel job's live status — phase, per-gate progress, and the result when done."""

    job_id: str
    edge_id: str
    phase: RunPhase = RunPhase.QUEUED
    gates: list[GateProgress] = Field(default_factory=list)
    report: TestReport | None = None
    cone: Cone | None = None
    signature: str = ""
    error: str = ""
