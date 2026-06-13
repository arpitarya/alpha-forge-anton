"""Orff long-term memory — a user-editable context document injected into every
chat (the "project context" of the chat-app model, scoped to financial prefs).

Stored in the **elgar store**, not a plain home-dir file: the doc holds personal
goals and figures, exactly the money-adjacent data the `plan-store` rule keeps in
elgar (one git commit per edit, never in this public repo). Anton reaches it over
the shared `elgar` CLI — the same write path the operator uses. Read/write are
best-effort so a missing or absent store never blocks the chat stream."""

from __future__ import annotations

from app.modules.plans import elgar_bridge

# The doc id under which the concierge context lives in the elgar store.
MEMORY_DOC_ID = "orff-context"
MAX_CHARS = 4_000

MEMORY_PREAMBLE = (
    "User-maintained context (goals, constraints, preferences) — the user wrote "
    "and approved this; treat it as standing instructions for every reply:\n\n"
)


async def load_memory() -> str:
    """The memory doc, or "" when none exists — additive, never blocks a chat."""
    try:
        text = await elgar_bridge.get(MEMORY_DOC_ID)
    except Exception:
        return ""
    return (text or "").strip()[:MAX_CHARS]


async def save_memory(text: str) -> str:
    """Persist the doc into elgar (clipped to MAX_CHARS); returns what was stored."""
    clipped = text[:MAX_CHARS]
    await elgar_bridge.save(MEMORY_DOC_ID, clipped, message="orff: update context")
    return clipped
