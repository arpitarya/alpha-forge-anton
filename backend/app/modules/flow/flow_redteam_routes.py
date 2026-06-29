"""Red-team endpoints — start the LLM critique for a surviving edge, poll the result.

The route assembles the deterministic evidence (the run's `TestReport` + cone + the sizing
recommendation) and hands it to the model read-only — the LLM never recomputes a number.
Gated: red-team unlocks only for a PASSING edge with a completed run. The ONLY LLM path in
the flow; it is cage-metered by the gateway and OFF the deterministic funnel/number path.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.modules.flow import flow_jobs, flow_redteam, flow_service, flow_sizing
from app.modules.flow.flow_redteam_schema import RedteamContext, RedteamReport
from app.modules.flow.flow_run_schema import RunPhase
from app.modules.flow.flow_sizing_schema import SizingInputs

router = APIRouter()


async def _context(edge_id: str) -> RedteamContext:
    flow = await flow_service.load_flow(edge_id)
    if flow is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"unknown edge {edge_id!r}")
    run = flow_jobs.latest_for(edge_id)
    if run is None or run.phase != RunPhase.DONE or run.report is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "run the Test stage first")
    if run.report.verdict != "pass":
        raise HTTPException(status.HTTP_409_CONFLICT, "red-team unlocks only for a surviving edge")
    sizing = flow_sizing.size(SizingInputs())
    cone = run.cone
    return RedteamContext(
        edge_id=edge_id,
        hypothesis=flow.hypothesis,
        verdict=run.report.verdict,
        gates_passed=run.report.gates_passed,
        pbo=run.report.pbo,
        deflated_sharpe=run.report.deflated_sharpe,
        haircut_t=run.report.haircut_t,
        pct_windows_positive=run.report.walkforward.pct_windows_positive,
        es_p5=cone.es_p5 if cone else 0.0,
        horizon=cone.horizon if cone else "",
        recommended_pct=sizing.recommended_pct,
        binding=sizing.binding,
    )


@router.post("/edges/{edge_id}/redteam", response_model=RedteamReport, status_code=202)
async def start_redteam(edge_id: str) -> RedteamReport:
    """Start (or rejoin) the cage-metered red-team for a surviving edge."""
    return flow_redteam.start(await _context(edge_id))


@router.get("/edges/{edge_id}/redteam", response_model=RedteamReport | None)
async def get_redteam(edge_id: str) -> RedteamReport | None:
    """The latest red-team report for an edge (null until it has been run this session)."""
    return flow_redteam.get(edge_id)
