"""The outcome cone — a forward distribution shown downside-first.

Every forward projection Orff presents is a cone, never a point estimate, and the
worst-case (`es_p5`, the expected shortfall of the 5th-percentile tail) leads. `stale`
flags a cone built on a feed that is no longer live — an honest cone is never silently
presented as fresh. Series are p5/p50/p95 paths aligned 1:1 over the horizon.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Cone(BaseModel):
    """A forward outcome cone — downside-first, staleness-honest."""

    horizon: str = ""
    p5: list[float] = Field(default_factory=list)
    p50: list[float] = Field(default_factory=list)
    p95: list[float] = Field(default_factory=list)
    es_p5: float = 0.0  # expected shortfall of the worst 5% — the downside-first number
    confidence: float = 0.0
    stale: bool = False
