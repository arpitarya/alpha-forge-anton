"""Plan-stage endpoint — deterministic position sizing for a surviving edge.

Stateless and pure: the sizing math depends only on the inputs (the human's capital +
risk knobs, mandate-aligned defaults), never on a clock or a live feed. It is SHOWN for
approval, never auto-applied and never an order. Auth-gated like the rest of `/flow`.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.flow import flow_sizing
from app.modules.flow.flow_sizing_schema import SizingInputs, SizingResult

router = APIRouter()


@router.post("/sizing", response_model=SizingResult)
async def compute_sizing(inputs: SizingInputs) -> SizingResult:
    """Size a position four ways (fixed-risk · downside cap · ADV cap · fractional-Kelly);
    the binding minimum is the recommendation. Deterministic, $0, shown — never applied."""
    return flow_sizing.size(inputs)
