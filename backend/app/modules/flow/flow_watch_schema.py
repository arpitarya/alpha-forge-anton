"""Watch-stage shapes — the live-edge decay monitor and the decay-kill.

`watch-and-learn`: a live edge is monitored against the expectation it was approved on. Decay
signals are DETERMINISTIC ($0, no LLM) — realized expectancy collapsing, a drawdown breaching the
-12 / -20 guard, a losing streak. When the edge has decayed, the monitor recommends a decay-kill;
retiring it journals a `RetirementRecord` to elgar (the frozen pre-registered spec is untouched).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DecaySeverity(StrEnum):
    HIGH = "high"
    MED = "med"
    LOW = "low"


class WatchVerdict(StrEnum):
    HEALTHY = "healthy"
    DECAYING = "decaying"
    DECAYED = "decayed"  # decay-kill recommended


class Observation(BaseModel):
    """One realized period of the live edge — entered by the human (no live-P&L source yet)."""

    period: str
    return_pct: float  # realized net return for the period, %


class DecaySignal(BaseModel):
    """One deterministic decay signal — severity-tagged so the worst leads."""

    severity: DecaySeverity = DecaySeverity.MED
    name: str
    detail: str = ""


class WatchState(BaseModel):
    """The monitor's read-back — realized stats vs expectation, decay signals, and the verdict."""

    n_periods: int = 0
    realized_expectancy: float = 0.0  # mean realized return % per period
    hit_rate: float = 0.0
    max_dd: float = 0.0  # deepest peak-to-trough of the cumulative realized curve, %
    expected_expectancy: float = 0.0  # what the edge was approved on (from the spec)
    signals: list[DecaySignal] = Field(default_factory=list)
    verdict: WatchVerdict = WatchVerdict.HEALTHY
    kill_recommended: bool = False


class WatchRequest(BaseModel):
    """The realized series the human logs for the monitor to analyse (stateless)."""

    observations: list[Observation] = Field(default_factory=list)


class DecayKillRequest(BaseModel):
    """Retire a decayed edge — the realized series + the PII-guarded reason, in one body."""

    observations: list[Observation] = Field(default_factory=list)
    reason: str = ""


class RetirementRecord(BaseModel):
    """The persisted decay-kill — why the edge was retired, and when."""

    edge_id: str
    reason: str = ""
    realized_expectancy: float = 0.0
    max_dd: float = 0.0
    retired_at: str = ""  # ISO UTC — server-stamped
    ref: str | None = None  # elgar://plan/<id>
