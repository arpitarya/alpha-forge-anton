"""Objective loading — split from `objective_config` for the line budget.

Resolution: elgar `strategy/objective.md` → repo seed `objective.md` → `Objective()`
defaults. Re-exported by `objective_config`; import `load_objective` from there.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from app.core.paths import elgar_dir
from app.modules.signals.objective_config import Objective

logger = logging.getLogger(__name__)

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


def _parse(text: str) -> dict:
    m = _FRONTMATTER.search(text) or _YAML_BLOCK.search(text)
    return yaml.safe_load(m.group(1) if m else text) or {}


def _objective_paths() -> tuple[Path, Path]:
    here = Path(__file__).resolve().parent
    return elgar_dir() / "strategy" / "objective.md", here / "objective.md"


def load_objective() -> Objective:
    """Typed objective from elgar → repo seed → defaults; parse errors fall through."""
    for path in _objective_paths():
        try:
            if path.exists():
                return Objective(**_parse(path.read_text()))
        except Exception as e:
            logger.warning("objective at %s unreadable (%s) — falling through", path, e)
    return Objective()
