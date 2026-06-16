"""Trusted-lane (claude-sdk) model + thinking tier — Phase 4.

Intent routing picks the Claude model and whether to think; the Think-harder toggle
(auto/on/off) overrides the thinking gate. Tiers are authored in routing.json, never
hardcoded here. Non-trusted lanes and explicit model pins pass through unchanged.
"""
from __future__ import annotations

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import QueryType

_TRUSTED = "claude-sdk"
_FORCE = {"on": True, "off": False}  # toggle overrides; "auto" → intent routing


def resolve(
    thinking_mode: str, intent_qt: QueryType, preferred: str | None, model: str | None
) -> tuple[str | None, bool, str | None]:
    """Return (model, reasoning, effort) for the lane. Honours an explicit Claude pin."""
    if preferred != _TRUSTED:
        return model, False, None
    reasoning = _FORCE.get(thinking_mode, registry.is_reasoning_intent(intent_qt))
    effort = registry.effort_for(_TRUSTED, intent_qt.value) if reasoning else None
    return model or registry.model_for(_TRUSTED, intent_qt.value), reasoning, effort
