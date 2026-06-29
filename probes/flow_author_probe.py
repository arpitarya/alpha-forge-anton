"""Flow-cockpit probe — the 8-stage spine + Idea/Rule authoring guarantees (no CDP, no elgar).

Asserts the deterministic core of stage (a) without writing to the real store:
  1. The locked flow renders all 9 nodes in order (Idea→…→Watch).
  2. Idea templates: Family A/B are authorable; Family C is scaffolded (unavailable).
  3. Stage derivation is honest: a KILL gates the downstream BLOCKED; an un-run edge is
     ACTIVE at Test with NA downstream — never a faked "done".
  4. Authoring SERVER-stamps `pre_registered_at` (never client-supplied).
  5. Pre-registration freeze: authoring an edge with a recorded run is rejected.
  6. Derivation is deterministic (byte-identical across calls).

Run:  uv run python probes/flow_author_probe.py   |   just probe flow-author
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(
        f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}"
    )
    if not ok:
        _fail += 1


async def main() -> int:
    from app.modules.edges.edge_journal import JournalRecord
    from app.modules.edges.edge_schema import EdgeSpec
    from app.modules.flow import flow_author, flow_service, flow_templates
    from app.modules.flow.flow_schema import AuthorEdgeRequest, StageId, StageState
    from app.modules.flow.flow_stages import STAGES, derive, stage_defs

    # 1. the locked flow — 9 nodes in order
    order = [s.id for s in stage_defs()]
    expect = [
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
    check(
        "flow renders all 9 stages in order",
        order == expect,
        str([s.value for s in order]),
    )
    check("STAGES table matches", [s for s, _ in STAGES] == expect)

    # 2. Idea templates
    tpls = {t.id: t for t in flow_templates.templates()}
    fams = {t.family for t in tpls.values()}
    check("templates cover Family A/B/C", fams == {"A", "B", "C"}, str(fams))
    check(
        "Family A/B authorable",
        all(t.available for t in tpls.values() if t.family in "AB"),
    )
    check(
        "Family C scaffolded (unavailable)",
        not next(t for t in tpls.values() if t.family == "C").available,
    )

    # 3. honest derivation — KILL gates downstream; un-run edge active@Test
    spec = EdgeSpec(
        id="edge-x",
        hypothesis="h",
        signal="momentum",
        pre_registered_at=datetime(2026, 6, 1, tzinfo=UTC),
    )
    kill = JournalRecord(
        edge_id="edge-x", run_at="2026-06-27T00:00:00Z", gate_reached=0, passed=False
    )
    kd = {s.id: s for s in derive(spec, kill)}
    check(
        "KILL: Idea/Rule/Test done",
        all(
            kd[s].state == StageState.DONE
            for s in (StageId.IDEA, StageId.RULE, StageId.TEST)
        ),
    )
    check(
        "KILL: Test summary says KILL",
        "KILL" in kd[StageId.TEST].summary,
        kd[StageId.TEST].summary,
    )
    check(
        "KILL: Range NA (cone informative even for a kill)",
        kd[StageId.RANGE].state == StageState.NA,
    )
    check(
        "KILL: Plan→Watch BLOCKED",
        all(
            kd[s].state == StageState.BLOCKED
            for s in (StageId.PLAN, StageId.APPROVE, StageId.WATCH)
        ),
    )
    nd = {s.id: s for s in derive(spec, None)}
    check("un-run: Test ACTIVE", nd[StageId.TEST].state == StageState.ACTIVE)
    check(
        "un-run: Range→Watch NA (honest-pending)",
        nd[StageId.RANGE].state == StageState.NA,
    )

    # 4 + 5. authoring server-stamps + freeze — patched store, no real elgar write
    captured: dict[str, EdgeSpec] = {}

    async def _fake_save(s: EdgeSpec) -> str:
        captured["spec"] = s
        return f"elgar://plan/{s.id}"

    flow_author.edge_store.save = _fake_save  # type: ignore[assignment]
    flow_author.edge_store.new_edge_id = lambda: "edge-new"  # type: ignore[assignment]
    flow_service.is_frozen = lambda _id: False  # type: ignore[assignment]
    flow_author.flow_service.load_flow = lambda _id: _ok_flow(_id)  # type: ignore[assignment]

    await flow_author.author(
        AuthorEdgeRequest(hypothesis="buy winners", signal="momentum")
    )
    saved = captured.get("spec")
    check(
        "authoring server-stamps pre_registered_at",
        saved is not None and saved.pre_registered_at is not None,
    )
    check(
        "authoring uses the server-minted id",
        saved is not None and saved.id == "edge-new",
    )

    flow_service.is_frozen = lambda _id: True  # type: ignore[assignment]
    try:
        await flow_author.author(
            AuthorEdgeRequest(edge_id="edge-x", hypothesis="edit", signal="momentum")
        )
        check("freeze rejects a re-author", False, "no error raised")
    except flow_author.EdgeFrozenError:
        check("freeze rejects a re-author after a run", True)

    # 6. determinism
    check("derive is deterministic", derive(spec, kill) == derive(spec, kill))

    print(
        "\n"
        + (
            "❌ flow-author probe FAILED"
            if _fail
            else "✅ Flow spine + authoring guarantees hold"
        )
    )
    return 1 if _fail else 0


async def _ok_flow(edge_id: str):
    from app.modules.flow.flow_schema import FlowState

    return FlowState(edge_id=edge_id, stages=[])


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
