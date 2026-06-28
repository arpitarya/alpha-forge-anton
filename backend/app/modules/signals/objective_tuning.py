"""Propose + apply an objective change — the conversational north-star tuning path.

Orff emits an ApprovalCard; only on user confirmation does this module write the
objective into the elgar `strategy` collection that load_objective reads — through
the elgar API (`elgar_bridge.save`), which git-commits and fail-loud-validates the
store. Anton owns no store path; a bad/unreachable store raises (never a silent write).
"""
from __future__ import annotations

from typing import Literal

import yaml
from pydantic import BaseModel

from app.modules.plans import elgar_bridge
from app.modules.signals.objective_config import Objective
from app.modules.signals.objective_loader import load_objective


class ObjectiveUpdate(BaseModel):
    monthly_target_inr: float | None = None
    horizon: Literal["swing", "long_term"] | None = None
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] | None = None
    mission: str | None = None


def _to_md(obj: Objective) -> str:
    body = yaml.safe_dump(obj.model_dump(mode="json"), sort_keys=False)
    return f"---\n{body}---\n\n# Objective (Orff-tuned)\n"


async def apply(payload: dict) -> Objective:
    """Merge payload into the objective, save via the elgar API. Raises on bad values/store."""
    data = load_objective().model_dump(mode="json")
    data.update({k: v for k, v in payload.items() if v is not None})
    new = Objective(**data)  # ValidationError on bad fields
    await elgar_bridge.save(
        "objective", _to_md(new), message="orff: update objective", collection="strategy"
    )
    return new
