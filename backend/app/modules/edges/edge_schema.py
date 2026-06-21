"""Pydantic shapes for the edge-discovery engine — the pre-registered hypothesis.

`EdgeSpec` is the pre-registered hypothesis (its `pre_registered_at` is the discipline
anchor — see `edge_register`). `ResultStats` / `GateResult` carry no clock and no
nondeterministic field on purpose: the same spec + same bars must serialise
byte-identically (the determinism contract, mirroring `signal_schema.ActionPlan`).
The run timestamp lives on the journal record, never inside a gate result.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EdgeStatus(StrEnum):
    CANDIDATE = "candidate"  # pre-registered, not yet validated
    PAPER = "paper"  # cleared gates, paper-trading (later slice)
    LIVE = "live"  # real capital (later slice)
    RETIRED = "retired"  # killed or decayed


class EdgeSpec(BaseModel):
    """A pre-registered edge hypothesis. Lives in elgar; the repo holds only the link."""

    id: str
    hypothesis: str
    universe: list[str] = Field(default_factory=list)
    signal: str  # id into the deterministic signal registry (edge_signal)
    holding_period_days: int = 5
    expected_edge_pct: float = 0.0  # per-trade % after costs the author expects
    pre_registered_at: datetime | None = None  # MUST predate any recorded result
    status: EdgeStatus = EdgeStatus.CANDIDATE
    gate_reached: int = 0  # highest gate cleared so far (0 = none)


class ResultStats(BaseModel):
    """Deterministic backtest statistics — no clock, byte-identical across reruns."""

    trades: int = 0
    expectancy_pct: float = 0.0  # mean per-trade net % after costs (the edge)
    hit_rate: float = 0.0  # fraction of round-trips net-positive
    turnover: float = 0.0  # round-trips per year (short-horizon cost driver)
    max_dd_pct: float = 0.0  # deepest peak-to-trough on the cumulative net curve, %
    calmar: float = 0.0  # annualised return / max drawdown


class GateResult(BaseModel):
    """One gate's verdict for an edge — pass/kill plus the stats that decided it."""

    gate: int  # 1 = out-of-sample backtest, 2 = walk-forward
    passed: bool = False
    stats: ResultStats = Field(default_factory=ResultStats)
    windows: list[ResultStats] = Field(default_factory=list)  # per-window (gate 2)
    notes: list[str] = Field(default_factory=list)
