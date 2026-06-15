"""Propose + apply a strategy-config change — the conversational tuning path (§6.5).

Orff never mutates the strategy silently: a change is surfaced as an **ApprovalCard**
(reusing the `action_service` confirm shape) and only written on the user's approval.
On apply, the new config is written to the elgar `strategy/` copy that
`strategy_config.load_config` reads — by the exact path, then a git commit (one
commit = an audit trail of how the strategy evolved). Best-effort: a missing store
logs and degrades, never blocks. Writing the path directly (vs the elgar CLI) keeps
the write consistent with the sync file reader.
"""

from __future__ import annotations

import asyncio
import logging
import re

import yaml

from app.modules.signals.strategy_config import StrategyConfig, _config_paths, load_config

logger = logging.getLogger(__name__)

_CHANGE = re.compile(r"\b(?:set|change|make)\s+([a-z_]+\.[a-z_]+)\s+(?:to|=)\s+([\w.\-]+)", re.I)


def _coerce(raw: str) -> object:
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    try:
        return float(raw) if "." in raw else int(raw)
    except ValueError:
        return raw


def detect(text: str) -> dict | None:
    """An ApprovalCard when the user explicitly asks to set a `group.knob` value."""
    m = _CHANGE.search(text or "")
    return propose(m.group(1), _coerce(m.group(2))) if m else None


def _set(data: dict, dotted: str, value: object) -> None:
    node = data
    keys = dotted.split(".")
    for k in keys[:-1]:
        node = node[k]
    if keys[-1] not in node:
        raise KeyError(dotted)
    node[keys[-1]] = value


def propose(knob: str, value: object) -> dict:
    """An ApprovalCard payload for a strategy change — approve to apply, never silent."""
    return {
        "id": "strategy-" + knob.replace(".", "-"),
        "action": f"Set strategy {knob} = {value}",
        "summary": f"Tune the deterministic ruleset: {knob} → {value}. Effective next /review.",
        "steps": [
            "Validate the knob + value against the strategy schema",
            "Write strategy.config.md to the elgar store (one commit = audit trail)",
            "Future /review + /screen use the new value deterministically",
        ],
        "apply": {"path": "/api/v1/signals/strategy", "body": {"knob": knob, "value": value}},
    }


def _to_md(cfg: StrategyConfig) -> str:
    body = yaml.safe_dump(cfg.model_dump(mode="json"), sort_keys=False)
    return f"---\n{body}---\n\n# Strategy config (Orff-tuned)\n"


async def _git_commit(path) -> None:
    root = path.parents[1]  # <elgar>/strategy/strategy.config.md → <elgar>
    for args in (["add", str(path)], ["commit", "-m", "orff: tune strategy config"]):
        proc = await asyncio.create_subprocess_exec(
            "git",
            "-C",
            str(root),
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()


async def apply(knob: str, value: object) -> StrategyConfig:
    """Validate, write to the elgar strategy copy, commit. Raises on a bad knob/value."""
    data = load_config().model_dump(mode="json")
    _set(data, knob, value)  # KeyError on an unknown knob path
    new = StrategyConfig(**data)  # ValidationError on a bad value
    path = _config_paths()[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_to_md(new))
    try:
        await _git_commit(path)
    except Exception as e:  # commit is best-effort; the write already landed
        logger.warning("strategy config commit skipped: %s", e)
    return new
