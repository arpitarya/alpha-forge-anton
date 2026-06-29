"""In-memory async job registry for funnel runs — start, poll, no double-run.

A run is a background `asyncio.create_task`: the POST returns a `queued` status
immediately (never blocking), the heavy compute happens off the event loop (`flow_run`
uses a worker thread), and the cockpit polls `get(job_id)` until `done`/`failed`. One
run per edge at a time — `start` returns the in-flight job rather than launching a
second. Ephemeral by design (single-process, single user); the journal is the durable record.
"""

from __future__ import annotations

import asyncio
import uuid

from app.modules.flow import flow_run
from app.modules.flow.flow_run_schema import GateProgress, RunPhase, RunStatus

_JOBS: dict[str, RunStatus] = {}
_BY_EDGE: dict[str, str] = {}  # edge_id → latest job_id


def _pending_gates() -> list[GateProgress]:
    return [GateProgress(gate=g, label=label) for g, label in flow_run.GATES]


def get(job_id: str) -> RunStatus | None:
    return _JOBS.get(job_id)


def latest_for(edge_id: str) -> RunStatus | None:
    job_id = _BY_EDGE.get(edge_id)
    return _JOBS.get(job_id) if job_id else None


def is_running(edge_id: str) -> bool:
    status = latest_for(edge_id)
    return status is not None and status.phase in (RunPhase.QUEUED, RunPhase.RUNNING)


async def _execute(job_id: str, edge_id: str) -> None:
    status = _JOBS[job_id]
    status.phase = RunPhase.RUNNING
    try:
        result = await flow_run.run_edge(edge_id)
        status.report = result.report
        status.cone = result.cone
        status.signature = result.signature
        status.gates = flow_run.gates_from_report(result.report)
        status.phase = RunPhase.DONE
    except Exception as e:  # fail-loud into the status; never crash the loop
        status.error = str(e)
        status.phase = RunPhase.FAILED


def start(edge_id: str) -> RunStatus:
    """Start a funnel run (or return the in-flight one) — no double-run for an edge."""
    if (running := latest_for(edge_id)) is not None and is_running(edge_id):
        return running
    job_id = uuid.uuid4().hex[:12]
    status = RunStatus(
        job_id=job_id, edge_id=edge_id, phase=RunPhase.QUEUED, gates=_pending_gates()
    )
    _JOBS[job_id] = status
    _BY_EDGE[edge_id] = job_id
    asyncio.create_task(_execute(job_id, edge_id))  # noqa: RUF006 — registry holds the status, not the task
    return status
