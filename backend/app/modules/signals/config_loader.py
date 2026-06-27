"""Strategy-config loading — split from `strategy_config` for the line budget.

Resolution: elgar `strategy/` (live, Orff-editable) → git-safe repo seed
`strategy.config.md` → defaults; a parse error falls through. Re-exported by
`strategy_config`, so import `load_config` / `_config_paths` from there.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from app.core.paths import elgar_dir
from app.modules.signals.strategy_config import StrategyConfig

logger = logging.getLogger(__name__)

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


def _parse(text: str) -> dict:
    m = _FRONTMATTER.search(text) or _YAML_BLOCK.search(text)
    return yaml.safe_load(m.group(1) if m else text) or {}


def _config_paths() -> tuple[Path, Path]:  # (elgar live copy, repo seed)
    here = Path(__file__).resolve().parent
    return elgar_dir() / "strategy" / "strategy.config.md", here / "strategy.config.md"


def load_config() -> StrategyConfig:
    """Typed config from elgar → repo seed → defaults; a parse error falls through."""
    for path in _config_paths():
        try:
            if path.exists():
                return StrategyConfig(**_parse(path.read_text()))
        except Exception as e:  # a malformed copy degrades to the next source
            logger.warning("strategy config at %s is unreadable (%s) — falling through", path, e)
            continue
    return StrategyConfig()
