"""Idea-stage candidate templates — the starting points an author browses (find-ideas).

A template pre-fills the Rule-stage form; it is NOT itself pre-registered (the human
edits it, then authors). Family A (factor: interpretable cross-sectional ranking) and
Family B (risk-managed variant) map to real signals/configs the engine runs today.
Family C (event/news-driven) is SCAFFOLDED — `available=False` — its feed/engine is
deferred (out of scope, §3); it shows in the browser but cannot be authored yet.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.modules.edges.factor_schema import FactorConfig
from app.modules.flow.flow_schema import AuthorEdgeRequest


class EdgeTemplate(BaseModel):
    """One Idea-stage starting point — family, blurb, availability, and the form prefill."""

    id: str
    family: str  # "A" | "B" | "C"
    name: str
    description: str
    available: bool = True  # False → scaffolded, engine deferred (honest, not hidden)
    prefill: AuthorEdgeRequest


def templates() -> list[EdgeTemplate]:
    """The catalogue `/flow/templates` serves the Idea browser — deterministic, no I/O."""
    return [
        EdgeTemplate(
            id="tpl-a-momentum-quality",
            family="A",
            name="Cross-sectional momentum + quality",
            description="Rank the liquid universe by 12-1 momentum; keep the top slice passing a "
            "ROCE/D-E quality screen; hold while NIFTY ≥ 200-DMA. (edge-001 family.)",
            prefill=AuthorEdgeRequest(
                hypothesis="Recent winners that are financially strong outperform while the market "
                "trends up; rebalance weekly.",
                signal="momentum",
                holding_period_days=5,
                expected_edge_pct=0.0,
                factor=FactorConfig(),
            ),
        ),
        EdgeTemplate(
            id="tpl-b-volscaled-momentum",
            family="B",
            name="Risk-managed (vol-scaled) momentum",
            description="The same momentum core, position-scaled by inverse volatility to tame the "
            "momentum-crash path that breaches the drawdown guard. (edge-002 family.)",
            prefill=AuthorEdgeRequest(
                hypothesis="Vol-scaling the momentum sleeve cuts crash-path drawdown without "
                "surrendering the trend premium.",
                signal="momentum",
                holding_period_days=5,
                expected_edge_pct=0.0,
                factor=FactorConfig(stop_on=True, trend_on=True),
            ),
        ),
        EdgeTemplate(
            id="tpl-c-event-driven",
            family="C",
            name="Event / news-driven (scaffolded)",
            description="React to point-in-time filings/news. Engine + paid feed are DEFERRED — a "
            "scaffold only; it cannot be authored or run yet (honest-pending).",
            available=False,
            prefill=AuthorEdgeRequest(hypothesis="", signal="", holding_period_days=1),
        ),
    ]
