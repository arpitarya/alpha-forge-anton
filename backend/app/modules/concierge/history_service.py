"""Orff conversation history — each chat session persisted as one elgar doc.

The chat-app's conversation sidebar, but transcripts live in the **elgar store**
(git-versioned, private), not a DB — the same money-adjacent data the `plan-store`
rule keeps out of this repo. History gets its own store **collection** (`sessions/`,
separate from `plans/`), so chats never mix with money plans or show up in
`elgar list`. One doc per session, rewritten in place as the conversation grows, so
the store's git log is the conversation's own audit trail. All I/O is best-effort:
a missing store never blocks the chat.

A turns block is embedded as a machine-readable comment for lossless resume; the
markdown above it is the human/git-readable transcript.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

from app.modules.concierge.concierge_schemas import SessionDoc, SessionMeta, SessionTurn
from app.modules.concierge.stream_events import strip_tool_markup as _scrub
from app.modules.plans import elgar_bridge

# The store collection (subdir) chat history lives in — never `plans`.
SESSION_DIR = "sessions"
MAX_TURNS = 200
_TURNS_RE = re.compile(r"<!-- orff:turns\n(.*?)\n-->", re.DOTALL)
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def render_session(
    meta: SessionMeta,
    turns: list[SessionTurn],
    *,
    updated: str | None = None,
    source: str | None = None,
) -> str:
    """The on-disk session doc. `updated`/`source` let importers write deterministic,
    provenance-tagged docs (a stable `updated` keeps re-syncs from churning git)."""
    ts = updated or datetime.now(UTC).isoformat(timespec="seconds")
    front = ["---", f"id: {meta.id}", "status: active", f"updated: {ts}"]
    if source:
        front.append(f"source: {source}")
    front.append("---")
    # Scrub leaked tool-call markup so both the human transcript and machine resume block
    # persist clean (a text-emitted tool call must never round-trip).
    clean = [t.model_copy(update={"query": _scrub(t.query), "response": _scrub(t.response)})
             for t in turns]
    lines = [*front, f"# {meta.title or 'Untitled chat'}", ""]
    for t in clean:
        lines += [f"**You:** {t.query}", ""]
        if t.response:
            tag = " · ".join(x for x in (t.provider, t.model) if x)
            head = f"**Orff** ({tag}):" if tag else "**Orff:**"
            lines += [f"{head} {t.response}", ""]
    payload = json.dumps([t.model_dump() for t in clean], ensure_ascii=False)
    lines += [f"<!-- orff:turns\n{payload}\n-->", ""]
    return "\n".join(lines)


async def save_session(meta: SessionMeta, turns: list[SessionTurn]) -> str:
    """Write/overwrite a session's transcript in the sessions collection; returns its id."""
    body = render_session(meta, turns[-MAX_TURNS:])
    msg = f"orff: session {meta.id}"
    await elgar_bridge.save(meta.id, body, message=msg, collection=SESSION_DIR)
    return meta.id


async def load_session(session_id: str) -> SessionDoc:
    """Parse a stored session back into structured turns for resume (empty when absent)."""
    try:
        text = await elgar_bridge.get(session_id, collection=SESSION_DIR) or ""
    except Exception:
        text = ""
    m = _TURNS_RE.search(text)
    turns = [SessionTurn(**t) for t in json.loads(m.group(1))] if m else []
    title_m = _TITLE_RE.search(text)
    return SessionDoc(id=session_id, title=title_m.group(1).strip() if title_m else "", turns=turns)


async def list_sessions() -> list[SessionMeta]:
    """Past conversations (store-order), title-labelled for the sidebar."""
    try:
        rows = await elgar_bridge.list_docs(collection=SESSION_DIR)
    except Exception:
        return []
    return [SessionMeta(id=r["id"], title=r.get("title", "")) for r in rows]


async def delete_session(session_id: str) -> bool:
    """Remove a conversation from the store; False if it was already gone."""
    try:
        return await elgar_bridge.remove(session_id, collection=SESSION_DIR)
    except Exception:
        return False
