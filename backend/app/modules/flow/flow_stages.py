"""The locked process-flow stages + deterministic status derivation.

Pure functions, no I/O, no clock: given an `EdgeSpec` and the edge's latest journal
record (or None), derive each stage's `StageState`. This is the cockpit spine —
Idea/Rule/Test are real; Range = the cone; Plan unlocks on a PASS; Red-team→Watch render
honest-pending (NA), or BLOCKED when a KILL gates the downstream off.
"""

from __future__ import annotations

from app.modules.edges.edge_journal import JournalRecord
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.flow.flow_schema import StageId, StageState, StageStatus

# The locked flow, in order — (id, label). Idea→Rule→Test→Range→Plan→Red-team→Approve→Live→Watch.
STAGES: list[tuple[StageId, str]] = [
    (StageId.IDEA, "Idea"),
    (StageId.RULE, "Rule"),
    (StageId.TEST, "Test"),
    (StageId.RANGE, "Range"),
    (StageId.PLAN, "Plan"),
    (StageId.REDTEAM, "Red-team"),
    (StageId.APPROVE, "Approve"),
    (StageId.LIVE, "Live"),
    (StageId.WATCH, "Watch"),
]
_LABEL = dict(STAGES)


def _st(sid: StageId, state: StageState, summary: str = "") -> StageStatus:
    return StageStatus(id=sid, label=_LABEL[sid], state=state, summary=summary)


def stage_defs() -> list[StageStatus]:
    """Static stage metadata (no edge) — what `/flow/stages` serves the rail skeleton."""
    return [_st(sid, StageState.PENDING) for sid, _ in STAGES]


def _rule_status(spec: EdgeSpec) -> StageStatus:
    pre = spec.pre_registered_at
    if pre is None:
        return _st(StageId.RULE, StageState.ACTIVE, "draft — not yet pre-registered")
    return _st(StageId.RULE, StageState.DONE, f"pre-registered {pre.date().isoformat()} · frozen")


def _test_status(rec: JournalRecord | None) -> StageStatus:
    if rec is None:
        return _st(StageId.TEST, StageState.ACTIVE, "ready to run — Test stage lands next")
    verdict = "PASS" if rec.passed else "KILL"
    return _st(StageId.TEST, StageState.DONE, f"Gate {rec.gate_reached} · {verdict}")


# Stages that UNLOCK on a PASS (built + reachable for a surviving edge): id → active-summary.
_ON_PASS = {
    StageId.PLAN: "sizing available — fixed-risk · downside · ADV · Kelly",
    StageId.REDTEAM: "red-team available — evidence critic + 10th-Man (LLM, cage-metered)",
    StageId.APPROVE: "decision available — downside-first, ack-loss-first, journaled to elgar",
    StageId.LIVE: "orders available once approved — copy-only, human-placed, never auto-executed",
    StageId.WATCH: "decay monitor available — performance, decay signals, decay-kill",
}


def _gated_status(sid: StageId, rec: JournalRecord | None, killed: bool) -> StageStatus:
    # ACTIVE only for a SURVIVING edge; BLOCKED for a kill; NA (not built) for an un-run edge.
    if rec and rec.passed:
        return _st(sid, StageState.ACTIVE, _ON_PASS[sid])
    if killed:
        return _st(sid, StageState.BLOCKED, "edge KILLed — downstream gated")
    return _st(sid, StageState.NA, "unlocks when the edge survives Test")


def derive(spec: EdgeSpec, rec: JournalRecord | None) -> list[StageStatus]:
    """The 9 stage statuses for one edge — deterministic, honest-pending downstream."""
    killed = rec is not None and not rec.passed
    # Range (the cone) is never gated by a KILL — it's informative even for a dead edge.
    cone = "Gate-3 cone" if rec else "outcome cone available — run Test to compute"
    return [
        _st(StageId.IDEA, StageState.DONE, "candidate authored"),
        _rule_status(spec),
        _test_status(rec),
        _st(StageId.RANGE, StageState.NA, cone),
        *(_gated_status(sid, rec, killed) for sid in _ON_PASS),  # Plan→Watch unlock on a PASS
    ]


def furthest(stages: list[StageStatus]) -> StageId:
    """The last stage that is DONE (or the first ACTIVE) — the edge's place in the flow."""
    active = [s for s in stages if s.state == StageState.ACTIVE]
    if active:
        return active[0].id
    done = [s for s in stages if s.state == StageState.DONE]
    return done[-1].id if done else StageId.IDEA
