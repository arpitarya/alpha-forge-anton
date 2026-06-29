"""Flow cockpit — the 8-stage view over an edge, and the authoring freeze.

Pins the deterministic spine (no elgar I/O): the locked 9-node order, honest status
derivation (a KILL gates the downstream BLOCKED; an un-run edge is ACTIVE at Test with
NA downstream — never a faked "done"), server-stamped pre-registration, and the
pre-registration freeze (re-authoring an edge with a recorded run is rejected).

    uv run pytest tests/test_flow_stages.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow import flow_author, flow_service
from app.modules.flow.flow_schema import AuthorEdgeRequest, StageId, StageState
from app.modules.flow.flow_stages import derive, stage_defs

_PRE = datetime(2026, 6, 1, tzinfo=UTC)
_SPEC = EdgeSpec(id="edge-x", hypothesis="h", signal="momentum", pre_registered_at=_PRE)
_KILL = JournalRecord(edge_id="edge-x", run_at="2026-06-27T00:00:00Z", gate_reached=0, passed=False)
_PASS = JournalRecord(edge_id="edge-x", run_at="2026-06-27T00:00:00Z", gate_reached=2, passed=True)


def test_locked_flow_has_nine_nodes_in_order():
    order = [s.id for s in stage_defs()]
    assert order == [
        StageId.IDEA,
        StageId.RULE,
        StageId.TEST,
        StageId.RANGE,
        StageId.PLAN,
        StageId.REDTEAM,
        StageId.APPROVE,
        StageId.LIVE,
        StageId.WATCH,
    ]


def test_kill_gates_plan_onward_but_not_range():
    st = {s.id: s for s in derive(_SPEC, _KILL)}
    assert st[StageId.TEST].state == StageState.DONE
    assert "KILL" in st[StageId.TEST].summary
    assert st[StageId.RANGE].state == StageState.NA  # the cone is informative even for a kill
    assert all(
        st[s].state == StageState.BLOCKED for s in (StageId.PLAN, StageId.APPROVE, StageId.WATCH)
    )


def test_unrun_edge_is_active_at_test_with_na_downstream():
    st = {s.id: s for s in derive(_SPEC, None)}
    assert st[StageId.TEST].state == StageState.ACTIVE
    assert st[StageId.RANGE].state == StageState.NA  # honest-pending, not faked


def test_pass_leaves_downstream_pending_not_blocked():
    st = {s.id: s for s in derive(_SPEC, _PASS)}
    assert st[StageId.TEST].state == StageState.DONE
    assert st[StageId.RANGE].state == StageState.NA


def test_derive_is_deterministic():
    assert derive(_SPEC, _KILL) == derive(_SPEC, _KILL)


@pytest.mark.asyncio
async def test_author_server_stamps_and_freeze_rejects(monkeypatch):
    captured: dict[str, EdgeSpec] = {}

    async def _save(spec: EdgeSpec) -> str:
        captured["spec"] = spec
        return f"elgar://plan/{spec.id}"

    async def _load(_id: str):  # read-back the freshly authored spec
        return captured["spec"]

    monkeypatch.setattr(flow_author.edge_store, "save", _save)
    monkeypatch.setattr(flow_author.edge_store, "load", _load)
    monkeypatch.setattr(flow_service, "is_frozen", lambda _id: False)

    req = AuthorEdgeRequest(edge_id="edge-new", hypothesis="buy", signal="momentum")
    flow = await flow_author.author(req)
    assert captured["spec"].pre_registered_at is not None  # SERVER-stamped, not client-set
    assert flow.edge_id == "edge-new"

    monkeypatch.setattr(flow_service, "is_frozen", lambda _id: True)
    with pytest.raises(flow_author.EdgeFrozenError):
        await flow_author.author(req)
