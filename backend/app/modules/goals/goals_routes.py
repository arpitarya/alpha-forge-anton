"""Goals-tab read endpoints — the live program mandate + the edge-library funnel.

Both are read-only and serve the Goals surface ([[GoalsPanel]]) with REAL data:
`/mandate` is the elgar-stored `Objective` (loaded at runtime, never committed),
`/edges/summary` is the discovery journal aggregated to counts only. A misconfigured
store surfaces as 503 rather than a faked default (fail-loud, `configurable-paths`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.modules.contracts.objective_contract import Objective
from app.modules.edges.edge_library import EdgeLibrarySummary, library_summary
from app.modules.goals.mandate_loader import load_mandate

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/mandate", response_model=Objective)
async def get_mandate() -> Objective:
    """The program mandate — Calmar bar, drawdown guard, self-funding, capital structure."""
    try:
        return load_mandate()
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e)) from e


@router.get("/edges/summary", response_model=EdgeLibrarySummary)
async def get_edges_summary() -> EdgeLibrarySummary:
    """Edge-library funnel from the journal: tested / killed / passed / live / kill_rate."""
    return library_summary()
