"""Red-team shapes — the ONLY LLM stage's output, OFF the deterministic number path.

The LLM critiques EVIDENCE; it never computes or alters a number. `RedteamContext` is the
deterministic evidence (verdict, overfitting stats, the cone's worst case, the recommended
size) assembled from the funnel/cone/sizing and handed to the model read-only. The model
returns a two-tier critique — an evidence critic (severity-tagged objections) plus a forced
10th-Man dissent — with runner-ups and tripwires. Advisory only; it gates nothing deterministic.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.modules.flow.flow_run_schema import RunPhase


class Severity(StrEnum):
    HIGH = "high"
    MED = "med"
    LOW = "low"


class RedteamObjection(BaseModel):
    """One evidence-critic objection — severity-tagged so the loudest risk leads."""

    severity: Severity = Severity.MED
    title: str
    detail: str = ""


class RedteamContext(BaseModel):
    """The deterministic evidence the model critiques — numbers in, never recomputed."""

    edge_id: str
    hypothesis: str = ""
    verdict: str = "pass"
    gates_passed: list[int] = Field(default_factory=list)
    pbo: float = 0.0  # probability of backtest overfitting
    deflated_sharpe: float = 0.0
    haircut_t: float = 0.0  # multiple-testing haircut
    pct_windows_positive: float = 0.0  # walk-forward consistency
    es_p5: float = 0.0  # the cone's worst-case shortfall
    horizon: str = ""
    recommended_pct: float = 0.0  # sizing — position as % of capital
    binding: str = ""  # which sizing constraint bound


class RedteamReport(BaseModel):
    """The two-tier critique — advisory reasoning attached to a proposal, cage-metered."""

    phase: RunPhase = RunPhase.QUEUED
    objections: list[RedteamObjection] = Field(default_factory=list)  # tier 1, severity-sorted
    tenth_man: str = ""  # tier 2 — the forced dissent (strongest case against proceeding)
    runner_ups: list[str] = Field(default_factory=list)  # alternatives worth preferring
    tripwires: list[str] = Field(default_factory=list)  # live conditions that would invalidate it
    provider: str = ""  # metering attribution — which model spoke (cage records the cost)
    model: str = ""
    error: str = ""
