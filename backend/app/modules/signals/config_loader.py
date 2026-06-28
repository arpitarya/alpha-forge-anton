"""Strategy-config loading — split from `strategy_config` for the line budget.

Resolution: elgar `strategy/strategy.config` (via the elgar API — Anton owns no
store path) → git-safe repo seed `strategy.config.md` → defaults; a parse error
falls through. Re-exported by `strategy_config`, so import `load_config` from there.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from app.modules.plans import elgar_bridge
from app.modules.signals.strategy_config import StrategyConfig

logger = logging.getLogger(__name__)

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_YAML_BLOCK = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)


def _parse(text: str) -> dict:
    m = _FRONTMATTER.search(text) or _YAML_BLOCK.search(text)
    return yaml.safe_load(m.group(1) if m else text) or {}


def _seed() -> Path:
    return Path(__file__).resolve().parent / "strategy.config.md"


def load_config() -> StrategyConfig:
    """Typed config from elgar (API) → repo seed → defaults; a parse error falls through."""
    seed = _seed()
    sources = [
        elgar_bridge.get_sync("strategy.config", collection="strategy"),
        seed.read_text() if seed.exists() else None,
    ]
    for text in sources:
        if not text:
            continue
        try:
            return StrategyConfig(**_parse(text))
        except Exception as e:  # a malformed copy degrades to the next source
            logger.warning("strategy config source unreadable (%s) — falling through", e)
    return StrategyConfig()
