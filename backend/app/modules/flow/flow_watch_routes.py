"""Watch endpoints — analyse a live edge's realized series, and decay-kill a decayed one.

The decay analysis is deterministic ($0, no LLM, stateless — the human logs the realized
series). A decay-kill journals a retirement to elgar (fail-loud, PII-guarded reason) and never
mutates the frozen pre-registered spec. The expected expectancy comes from the edge's spec.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.flow import flow_service, flow_watch
from app.modules.flow.flow_watch_schema import (
    DecayKillRequest,
    RetirementRecord,
    WatchRequest,
    WatchState,
)
from app.modules.plans.elgar_bridge import ElgarStoreError

router = APIRouter()


async def _expected(edge_id: str) -> float:
    from app.modules.flow.flow_run import resolve_spec

    if await flow_service.load_flow(edge_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    spec = await resolve_spec(edge_id)
    return spec.expected_edge_pct if spec else 0.0


@router.post("/edges/{edge_id}/watch", response_model=WatchState)
async def post_watch(edge_id: str, req: WatchRequest) -> WatchState:
    """Decay read-back from the realized series — stats, signals, and the kill verdict."""
    return flow_watch.analyze(req.observations, await _expected(edge_id))


@router.post("/edges/{edge_id}/decay-kill", response_model=RetirementRecord, status_code=201)
async def post_decay_kill(edge_id: str, req: DecayKillRequest) -> RetirementRecord:
    """Retire a decayed edge — journals the decay-kill to elgar. Never mutates the frozen spec."""
    state = flow_watch.analyze(req.observations, await _expected(edge_id))
    try:
        return await flow_watch.retire(edge_id, req.reason, state)
    except flow_watch.DecayKillError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    except ElgarStoreError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
