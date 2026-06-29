"""Read side of the cockpit — list edges and assemble one edge's `FlowState`.

The honest source set is the UNION of (1) the discovery journal — every edge that has
RUN, keyed by its run `edge_id` (e.g. `edge-001`), whose embedded `TestReport` carries
`pre_registered_at` — and (2) UI-authored specs in the elgar `edges` collection that
round-trip through `edge_store` (a JSON-block doc). A hand-authored markdown spec with
no JSON block is not a machine edge and does not appear; the journal is the truth for
what ran. Fail-soft: a down store/journal yields an empty list, never a crash.
"""

from __future__ import annotations

from datetime import datetime

from app.modules.edges import edge_library, edge_store
from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow.flow_schema import EdgeListItem, FlowState
from app.modules.flow.flow_stages import derive, furthest


def latest_record(edge_id: str) -> JournalRecord | None:
    """The most recent journal run for an edge (None when it has never run)."""
    runs = [r for r in edge_library._records() if r.edge_id == edge_id]
    return max(runs, default=None, key=lambda r: r.run_at)


def is_frozen(edge_id: str) -> bool:
    """A spec is pre-registration-frozen once any run is recorded against it."""
    return latest_record(edge_id) is not None


def _synthetic_spec(rec: JournalRecord) -> EdgeSpec:
    """A minimal spec for a journal-only edge — its `pre_registered_at` is the run's anchor."""
    pre = (rec.report or {}).get("pre_registered_at")
    return EdgeSpec(
        id=rec.edge_id,
        hypothesis="",  # hand-authored markdown spec isn't machine-loadable — no faked text
        signal="",
        pre_registered_at=datetime.fromisoformat(pre) if pre else None,
    )


async def load_flow(edge_id: str) -> FlowState | None:
    """Assemble the cockpit state for one edge — spec + journal → 9 stage statuses."""
    rec = latest_record(edge_id)
    spec = await edge_store.load(edge_id) or (_synthetic_spec(rec) if rec else None)
    if spec is None:
        return None
    return FlowState(
        edge_id=spec.id,
        hypothesis=spec.hypothesis,
        frozen=rec is not None,
        spec_ref=f"elgar://edge/{spec.id}",
        stages=derive(spec, rec),
    )


async def _store_edge_ids() -> set[str]:
    """Edge ids of UI-authored specs that round-trip through `edge_store` (JSON-block docs)."""
    from app.modules.plans import elgar_bridge

    docs = await elgar_bridge.list_docs(collection="edges")
    ids = {d.get("id", "").removesuffix(".edge") for d in docs}
    return {i for i in ids if i and await edge_store.load(i) is not None}


async def list_edges() -> list[EdgeListItem]:
    """Every cockpit edge — journal plus UI-authored specs, id-deduped, with furthest stage."""
    journal_ids = {r.edge_id for r in edge_library._records()}
    out: list[EdgeListItem] = []
    for edge_id in sorted(journal_ids | await _store_edge_ids()):
        flow = await load_flow(edge_id)
        if flow:
            out.append(
                EdgeListItem(
                    edge_id=flow.edge_id,
                    hypothesis=flow.hypothesis,
                    frozen=flow.frozen,
                    stage=furthest(flow.stages),
                )
            )
    return out
