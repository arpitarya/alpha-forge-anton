"""Test-stage endpoints — start an async funnel run + poll its gate-by-gate progress.

The run is a background job (deterministic, $0, LLM-free): POST starts it and returns
immediately; the cockpit polls the status. No double-run — a second POST while a run is
in flight returns the same in-flight job. Auth-gated like the rest of `/flow`.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.flow import flow_jobs, flow_service
from app.modules.flow.flow_run_schema import RunStatus

router = APIRouter()


@router.post("/edges/{edge_id}/run", response_model=RunStatus, status_code=status.HTTP_202_ACCEPTED)
async def start_run(edge_id: str) -> RunStatus:
    """Start (or rejoin) the funnel run for an edge. 404 when the edge is unknown."""
    if await flow_service.load_flow(edge_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    return flow_jobs.start(edge_id)


@router.get("/runs/{job_id}", response_model=RunStatus)
async def get_run(job_id: str) -> RunStatus:
    """Poll one run's live status — phase, per-gate progress, report + cone when done."""
    run = flow_jobs.get(job_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown run {job_id!r}")
    return run


@router.get("/edges/{edge_id}/run", response_model=RunStatus | None)
async def latest_run(edge_id: str) -> RunStatus | None:
    """The latest in-session run for an edge (null when it hasn't been run this session)."""
    return flow_jobs.latest_for(edge_id)
