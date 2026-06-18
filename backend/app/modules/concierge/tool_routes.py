"""Tool-mutation endpoints — the apply targets for Orff ApprovalCard confirm cards.

These are called ONLY after the user approves a card. Each performs a server-side
read-modify-write so the frontend never merges authoritative content.
POST (not PUT) — neither append nor add/remove is idempotent.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.modules.concierge.critic_guard import ForbiddenRuntimeActionError
from app.modules.concierge.deep_search_service import run as run_deep_search
from app.modules.concierge.exclusion_service import apply as apply_exclusion
from app.modules.concierge.memory_service import append_memory

router = APIRouter(dependencies=[Depends(get_current_user)])


class _AppendBody(BaseModel):
    note: str


class _ExclusionBody(BaseModel):
    add: str | None = None
    remove: str | None = None


class _DeepSearchBody(BaseModel):
    queries: list[str]


@router.post("/memory/append")
async def post_memory_append(body: _AppendBody) -> dict:
    """Append a note to orff-context (apply target for update_context confirm card).

    The runtime money/PII guard (`runtime-note-pii`) refuses a note carrying a hard identifier
    (PAN / Aadhaar / account number) with a 422 — the write never reaches the elgar store."""
    try:
        content = await append_memory(body.note)
    except ForbiddenRuntimeActionError as e:
        raise HTTPException(422, f"refused: {e}") from e
    return {"content": content}


@router.post("/exclusion")
async def post_exclusion(body: _ExclusionBody) -> dict:
    """Add/remove a symbol from hard-exclusion-list (apply target for edit_exclusion_list)."""
    if not body.add and not body.remove:
        raise HTTPException(422, "body must have 'add' or 'remove'")
    sym, act = (body.add, "add") if body.add else (body.remove, "remove")
    try:
        content = await apply_exclusion(sym, act)
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    return {"result": "ok", "content": content}


@router.post("/deep-search")
async def post_deep_search(body: _DeepSearchBody) -> dict:
    """Run the confirmed deep-search queries (apply target for request_deep_search).
    One Parallel call per query → one Cage receipt each; fail-open to free sources."""
    return {"grounding": await run_deep_search(body.queries)}
