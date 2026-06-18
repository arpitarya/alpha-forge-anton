"""Orff long-term memory — a user-editable context document injected into every
chat (the "project context" of the chat-app model, scoped to financial prefs).

Stored in the **elgar store**, not a plain home-dir file: the doc holds personal
goals and figures, exactly the money-adjacent data the `plan-store` rule keeps in
elgar (one git commit per edit, never in this public repo). Anton reaches it over
the shared `elgar` CLI — the same write path the operator uses. Read/write are
best-effort so a missing or absent store never blocks the chat stream."""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.concierge.critic_guard import guard_note
from app.modules.plans import elgar_bridge

# The doc id the Memory panel reads/writes — the user's free-text additions.
MEMORY_DOC_ID = "orff-context"
MAX_CHARS = 8_000
CONTEXT_MAX = 12_000

# Standing-context docs injected into every chat, in priority order. These are the
# durable, FIGURE-FREE preference/rule docs — position figures never live here, they
# arrive live from the holdings disclosure (see the plan-store / secure-holdings rule).
# `orff-context` (last) holds the user's free-text additions from the Memory panel.
MEMORY_DOCS = (
    "investor-profile",
    "trading-sleeve-rules",
    "hard-exclusion-list",
    "portfolio-snapshot",
    "orff-context",
)

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


async def load_context() -> str:
    """Every standing-context doc concatenated (best-effort per doc) for prompt
    injection. The Memory panel still reads/writes only `orff-context` via
    load_memory/save_memory — this is the read-only union used at chat time."""
    out: list[str] = []
    for doc in MEMORY_DOCS:
        try:
            text = (await elgar_bridge.get(doc) or "").strip()
        except Exception:
            continue
        if text:
            out.append(f"## {doc}\n{text}")
    return "\n\n".join(out)[:CONTEXT_MAX]


async def save_memory(text: str) -> str:
    """Persist the doc into elgar (clipped to MAX_CHARS); returns what was stored."""
    clipped = text[:MAX_CHARS]
    await elgar_bridge.save(MEMORY_DOC_ID, clipped, message="orff: update context")
    return clipped


async def append_memory(note: str) -> str:
    """Append `note` to the memory doc with a date-stamp separator; returns new content.

    POST (not PUT) — calling twice must produce two entries, not one idempotent write.

    Runtime money/PII guard (`runtime-note-pii`): `guard_note` critiques the note BEFORE it is
    persisted — a deterministic PAN/Aadhaar/account match raises `ForbiddenRuntimeActionError`,
    so the elgar save never runs (runtime twin of `plan-store`). Judgment concerns are advisory.
    """
    await guard_note(note)
    current = await load_memory()
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    separator = f"\n\n---\n{stamp}\n"
    merged = (current + separator + note.strip())[:MAX_CHARS]
    return await save_memory(merged)
