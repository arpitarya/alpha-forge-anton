"""Propose + apply a strategy-config change — the conversational tuning path (§6.5).

Orff never mutates the strategy silently: a change is surfaced as an **ApprovalCard**
(reusing the `action_service` confirm shape) and only written on the user's approval.
On apply, the new config is saved into the elgar `strategy` collection that
`strategy_config.load_config` reads — through the elgar API (`elgar_bridge.save`),
which git-commits and fail-loud-validates the store. Anton owns no store path; a
bad/unreachable store raises (never a silent write).
"""

from __future__ import annotations

import re

import yaml

from app.modules.plans import elgar_bridge
from app.modules.signals.strategy_config import StrategyConfig, load_config

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


async def apply(knob: str, value: object) -> StrategyConfig:
    """Validate, save via the elgar API. Raises on a bad knob/value or unreachable store."""
    data = load_config().model_dump(mode="json")
    _set(data, knob, value)  # KeyError on an unknown knob path
    new = StrategyConfig(**data)  # ValidationError on a bad value
    await elgar_bridge.save(
        "strategy.config", _to_md(new), message="orff: tune strategy config", collection="strategy"
    )
    return new
