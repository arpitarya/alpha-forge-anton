"""Orff conversation history — each chat session persisted as one elgar doc.

The chat-app's conversation sidebar, but transcripts live in the **elgar store**
(git-versioned, private), not a DB — the same money-adjacent data the `plan-store`
rule keeps out of this repo. One doc per session (`orff-session-<id>`), rewritten
in place as the conversation grows, so the store's git log is the conversation's
own audit trail. All I/O is best-effort: a missing store never blocks the chat.

A turns block is embedded as a machine-readable comment for lossless resume; the
markdown above it is the human/git-readable transcript.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime

from app.modules.concierge.concierge_schemas import SessionDoc, SessionMeta, SessionTurn
from app.modules.plans import elgar_bridge

SESSION_PREFIX = "orff-session-"
MAX_TURNS = 200
_TURNS_RE = re.compile(r"<!-- orff:turns\n(.*?)\n-->", re.DOTALL)
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _doc_id(session_id: str) -> str:
    return f"{SESSION_PREFIX}{session_id}"


def _render(meta: SessionMeta, turns: list[SessionTurn]) -> str:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    lines = ["---", f"id: {_doc_id(meta.id)}", "status: active", f"updated: {now}", "---",
             f"# {meta.title or 'Untitled chat'}", ""]
    for t in turns:
        lines += [f"**You:** {t.query}", ""]
        if t.response:
            tag = " · ".join(x for x in (t.provider, t.model) if x)
            head = f"**Orff** ({tag}):" if tag else "**Orff:**"
            lines += [f"{head} {t.response}", ""]
    payload = json.dumps([t.model_dump() for t in turns], ensure_ascii=False)
    lines += [f"<!-- orff:turns\n{payload}\n-->", ""]
    return "\n".join(lines)


async def save_session(meta: SessionMeta, turns: list[SessionTurn]) -> str:
    """Write/overwrite a session's transcript in elgar; returns the session id."""
    clipped = turns[-MAX_TURNS:]
    body = _render(meta, clipped)
    await elgar_bridge.save(_doc_id(meta.id), body, message=f"orff: session {meta.id}")
    return meta.id


async def load_session(session_id: str) -> SessionDoc:
    """Parse a stored session back into structured turns for resume (empty when absent)."""
    try:
        text = await elgar_bridge.get(_doc_id(session_id)) or ""
    except Exception:
        text = ""
    m = _TURNS_RE.search(text)
    turns = [SessionTurn(**t) for t in json.loads(m.group(1))] if m else []
    title = (_TITLE_RE.search(text).group(1).strip() if _TITLE_RE.search(text) else "")
    return SessionDoc(id=session_id, title=title, turns=turns)


async def list_sessions() -> list[SessionMeta]:
    """Past conversations (newest store-order first), title-labelled for the sidebar."""
    try:
        rows = await elgar_bridge.list_docs(SESSION_PREFIX)
    except Exception:
        return []
    return [
        SessionMeta(id=r["id"].removeprefix(SESSION_PREFIX), title=r.get("title", "")) for r in rows
    ]


async def delete_session(session_id: str) -> bool:
    """Remove a conversation from the store; False if it was already gone."""
    try:
        return await elgar_bridge.remove(_doc_id(session_id))
    except Exception:
        return False
