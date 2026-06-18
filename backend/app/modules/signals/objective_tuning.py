"""Propose + apply an objective change — the conversational north-star tuning path.

Orff emits an ApprovalCard; only on user confirmation does this module write
objective.md to the elgar strategy/ copy that load_objective reads. Same write
pattern as strategy_tuning: direct file path write + git commit (one commit =
audit trail). Best-effort: commit failure logs and degrades, write already landed.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Literal

import yaml
from pydantic import BaseModel

from app.modules.signals.objective_config import Objective
from app.modules.signals.objective_loader import _objective_paths, load_objective

logger = logging.getLogger(__name__)


class ObjectiveUpdate(BaseModel):
    monthly_target_inr: float | None = None
    horizon: Literal["swing", "long_term"] | None = None
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] | None = None
    mission: str | None = None


def _to_md(obj: Objective) -> str:
    body = yaml.safe_dump(obj.model_dump(mode="json"), sort_keys=False)
    return f"---\n{body}---\n\n# Objective (Orff-tuned)\n"


async def _git_commit(path) -> None:
    root = path.parents[1]  # <elgar>/strategy/objective.md → <elgar>
    for args in (["add", str(path)], ["commit", "-m", "orff: update objective"]):
        proc = await asyncio.create_subprocess_exec(
            "git", "-C", str(root), *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()


async def apply(payload: dict) -> Objective:
    """Merge payload into the current objective, write to elgar, commit. Raises on bad values."""
    data = load_objective().model_dump(mode="json")
    data.update({k: v for k, v in payload.items() if v is not None})
    new = Objective(**data)  # ValidationError on bad fields
    path = _objective_paths()[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_to_md(new))
    try:
        await _git_commit(path)
    except Exception as e:
        logger.warning("objective commit skipped: %s", e)
    return new
