"""Rule-stage authoring — build a pre-registered `EdgeSpec` and write it to elgar.

This is how all future edges are created. The `pre_registered_at` is **server-stamped**
(`datetime.now(UTC)`) — never client-supplied — so the discipline anchor is trustworthy.
Pre-registration is frozen on first run: re-authoring an edge that already has a journal
record raises `EdgeFrozenError` (the spec must predate every result; `edge_register`).
The spec is money/strategy content → it lives in the private elgar store, link only here.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.edges import edge_store
from app.modules.edges.edge_schema import EdgeSpec, EdgeStatus
from app.modules.flow import flow_service
from app.modules.flow.flow_schema import AuthorEdgeRequest, FlowState


class EdgeFrozenError(RuntimeError):
    """Raised when an edge with a recorded run is re-authored (pre-registration freeze)."""


def _build_spec(req: AuthorEdgeRequest, edge_id: str, now: datetime) -> EdgeSpec:
    return EdgeSpec(
        id=edge_id,
        hypothesis=req.hypothesis,
        universe=req.universe,
        signal=req.signal,
        holding_period_days=req.holding_period_days,
        expected_edge_pct=req.expected_edge_pct,
        pre_registered_at=now,  # SERVER-stamped — the discipline anchor, never client-set
        status=EdgeStatus.CANDIDATE,
        factor=req.factor,
    )


async def author(req: AuthorEdgeRequest) -> FlowState:
    """Pre-register a new (or pre-run) edge to elgar and return its fresh `FlowState`."""
    edge_id = req.edge_id or edge_store.new_edge_id()
    if flow_service.is_frozen(edge_id):  # a run exists → spec is frozen, reject the edit
        raise EdgeFrozenError(
            f"edge {edge_id!r} has a recorded run — pre-registration is frozen, no edits allowed"
        )
    spec = _build_spec(req, edge_id, datetime.now(UTC))
    ref = await edge_store.save(spec)  # best-effort write; None when the store is unreachable
    if ref is None:
        raise RuntimeError("edge save failed — elgar store unreachable; nothing pre-registered")
    flow = await flow_service.load_flow(edge_id)
    if flow is None:  # save succeeded but read-back didn't — surface, never fabricate
        raise RuntimeError(f"edge {edge_id!r} saved but could not be loaded back")
    return flow
