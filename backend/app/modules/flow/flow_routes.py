"""Process-flow cockpit endpoints — the 8-stage spine + UI edge authoring.

Read paths (`/flow/stages|edges|templates`, `GET /flow/edges/{id}`) serve the cockpit
view over real edge state; the WRITE path (`POST /flow/edges`) pre-registers a new edge
to elgar with a SERVER-stamped timestamp, frozen on first run (422 on a frozen edit).
All are auth-gated; the funnel run itself is a later slice (stage Test), not here.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.modules.flow import (
    flow_approve_routes,
    flow_author,
    flow_live_routes,
    flow_redteam_routes,
    flow_run_routes,
    flow_service,
    flow_sizing_routes,
    flow_templates,
    flow_watch_routes,
)
from app.modules.flow.flow_schema import AuthorEdgeRequest, EdgeListItem, FlowState, StageStatus
from app.modules.flow.flow_stages import stage_defs

router = APIRouter(prefix="/flow", dependencies=[Depends(get_current_user)])
router.include_router(flow_run_routes.router)  # Test-stage run + status endpoints
router.include_router(flow_sizing_routes.router)  # Plan-stage deterministic sizing
router.include_router(flow_redteam_routes.router)  # Red-team — the only (cage-metered) LLM stage
router.include_router(flow_approve_routes.router)  # Approve — binary decision, journaled to elgar
router.include_router(flow_live_routes.router)  # Live — prepare orders + reconcile (NEVER places)
router.include_router(flow_watch_routes.router)  # Watch — deterministic decay monitor + decay-kill


@router.get("/stages", response_model=list[StageStatus])
async def get_stages() -> list[StageStatus]:
    """The locked 9-node flow skeleton (no edge) — labels + order for the rail."""
    return stage_defs()


@router.get("/templates", response_model=list[flow_templates.EdgeTemplate])
async def get_templates() -> list[flow_templates.EdgeTemplate]:
    """Idea-stage candidate templates (Family A/B real; C scaffolded, unavailable)."""
    return flow_templates.templates()


@router.get("/edges", response_model=list[EdgeListItem])
async def get_edges() -> list[EdgeListItem]:
    """Every cockpit edge — journal edges plus UI-authored specs, with their furthest stage."""
    return await flow_service.list_edges()


@router.get("/edges/{edge_id}", response_model=FlowState)
async def get_edge_flow(edge_id: str) -> FlowState:
    """One edge's 9-stage cockpit state. 404 when the edge is unknown."""
    flow = await flow_service.load_flow(edge_id)
    if flow is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    return flow


@router.post("/edges", response_model=FlowState, status_code=status.HTTP_201_CREATED)
async def author_edge(req: AuthorEdgeRequest) -> FlowState:
    """Author + pre-register a new edge to elgar (server-stamped). 422 if frozen by a run."""
    try:
        return await flow_author.author(req)
    except flow_author.EdgeFrozenError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    except RuntimeError as e:  # store unreachable / read-back failed — fail loud, never fake
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e
