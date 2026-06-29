"""Process-flow cockpit shapes — the 8-stage view over one edge's lifecycle.

`FlowState` is a *view* over edge state, not a new engine (the funnel/gates stay
server-side). Each stage maps to an artifact: Idea/Rule = the `EdgeSpec`, Test =
funnel gates, Range = cone, Plan = sizing, Red-team = critic, Approve = decision,
Live = order checklist, Watch = live series. `StageState` is honest by construction:
`pending`/`na` render where a stage isn't built-for-this-edge yet — never a faked number.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.modules.edges.factor_schema import FactorConfig


class StageId(StrEnum):
    IDEA = "idea"
    RULE = "rule"
    TEST = "test"
    RANGE = "range"
    PLAN = "plan"
    REDTEAM = "redteam"
    APPROVE = "approve"
    LIVE = "live"
    WATCH = "watch"


class StageState(StrEnum):
    DONE = "done"  # the stage's artifact exists for this edge
    ACTIVE = "active"  # the stage the edge is currently sitting at
    PENDING = "pending"  # built, but not yet reached for this edge
    NA = "na"  # not-built-for-this-edge yet (honest-pending; a later slice)
    BLOCKED = "blocked"  # gated shut (e.g. KILLed edge can't be approved)


class StageStatus(BaseModel):
    """One stage's verdict for an edge — id, label, state, one-line summary."""

    id: StageId
    label: str
    state: StageState = StageState.PENDING
    summary: str = ""


class FlowState(BaseModel):
    """The cockpit's per-edge state — 8 stages plus the freeze flag + elgar ref."""

    edge_id: str
    hypothesis: str = ""
    frozen: bool = False  # a run exists → spec is pre-registration-frozen (no edits)
    spec_ref: str | None = None  # elgar://edge/<id> (link only; doc lives off-repo)
    stages: list[StageStatus] = Field(default_factory=list)


class EdgeListItem(BaseModel):
    """One row in the cockpit's edge picker — id + hypothesis + freeze + furthest stage."""

    edge_id: str
    hypothesis: str = ""
    frozen: bool = False
    stage: StageId = StageId.RULE


class AuthorEdgeRequest(BaseModel):
    """The Rule-stage authoring form payload — the fields the engine consumes today.

    Sizing/exit-beyond-stop/rebalance-cadence are later-stage artifacts and stay
    out of the pre-registered spec here (rendered honest-pending in the cockpit).
    """

    edge_id: str | None = None  # None → server mints one
    hypothesis: str
    universe: list[str] = Field(default_factory=list)
    signal: str = "momentum"
    holding_period_days: int = 5
    expected_edge_pct: float = 0.0
    factor: FactorConfig | None = None
