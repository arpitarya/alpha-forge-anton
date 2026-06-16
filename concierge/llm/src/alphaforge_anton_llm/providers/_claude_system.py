"""System-prompt block builder for the Anthropic adapter — Phase 3 prompt caching.

The turn-stable blocks (SYSTEM + objective + memory, flagged `cacheable`) form a
contiguous prefix with one `cache_control` breakpoint on the last of them; volatile
blocks (Fux grounding, web, signals, live holdings) follow uncached. Caching is a
prefix match, so the cacheable run must come first and stay byte-stable across turns.
"""

from __future__ import annotations

from alphaforge_anton_llm.types import Message


def system_blocks(messages: list[Message]) -> list[dict] | None:
    """The `system` param as an Anthropic text-block array (cacheable-first), or None."""
    syst = [m for m in messages if m.role == "system"]
    if not syst:
        return None
    blocks = [{"type": "text", "text": m.content} for m in syst if m.cacheable]
    if blocks:
        blocks[-1]["cache_control"] = {"type": "ephemeral"}
    blocks += [{"type": "text", "text": m.content} for m in syst if not m.cacheable]
    return blocks
