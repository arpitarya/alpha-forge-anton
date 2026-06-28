"""Objective loading — split from `objective_config` for the line budget.

Resolution: elgar `strategy/objective` (via the elgar API — Anton owns no store
path) → repo seed `objective.md` → `Objective()` defaults. Re-exported by
`objective_config`; import `load_objective` from there.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from app.modules.plans import elgar_bridge
from app.modules.signals.objective_config import Objective

logger = logging.getLogger(__name__)

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


def _parse(text: str) -> dict:
    m = _FRONTMATTER.search(text) or _YAML_BLOCK.search(text)
    return yaml.safe_load(m.group(1) if m else text) or {}


def _seed() -> Path:
    return Path(__file__).resolve().parent / "objective.md"


def load_objective() -> Objective:
    """Typed objective from elgar (API) → repo seed → defaults; parse errors fall through."""
    seed = _seed()
    sources = [
        elgar_bridge.get_sync("objective", collection="strategy"),
        seed.read_text() if seed.exists() else None,
    ]
    for text in sources:
        if not text:
            continue
        try:
            return Objective(**_parse(text))
        except Exception as e:  # a malformed source degrades to the next
            logger.warning("objective source unreadable (%s) — falling through", e)
    return Objective()
