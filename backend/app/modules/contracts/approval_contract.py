"""The approval proposal — what Orff puts in front of the human before any action.

Downside-first by construction: `expected_shortfall` is the LARGEST loss the proposal
must justify (the required number), shown before the median upside. A red-team list and a
`tenth_man` dissent are mandatory devil's-advocate fields; `runner_ups` keep the rejected
alternatives visible; `tripwires` are the pre-committed exit conditions. `calibration`
carries the running scoreboard so the human can see whether past proposals cleared.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Calibration(BaseModel):
    """Running scoreboard of how prior proposals resolved."""

    cleared: int = 0  # reached the cone / thesis played out
    hit_stop: int = 0  # stopped out
    open: int = 0  # still live


class ApprovalProposal(BaseModel):
    """A single proposed action, framed downside-first for human approval."""

    thesis: str = ""
    notional: float = 0.0
    expected_shortfall: float = 0.0  # LARGEST loss / required — shown first
    median: float = 0.0
    stress: float = 0.0  # outcome under the stress scenario
    red_team: list[str] = Field(default_factory=list)
    tenth_man: str = ""  # the mandatory dissent
    runner_ups: list[str] = Field(default_factory=list)
    tripwires: list[str] = Field(default_factory=list)
    calibration: Calibration = Field(default_factory=Calibration)
    cooldown_s: int = 0  # enforced wait before this can be re-proposed
