"""Persist the approve/veto decision to the elgar `decisions` collection — FAIL-LOUD.

A decision is the human's recorded call; it MUST land or the human must know it didn't.
Unlike best-effort discovery writes, this does NOT swallow a store error — `elgar_bridge.save`
raises `ElgarStoreError` on an unreachable/invalid store and we let it propagate (the route
turns it into a 503). The repo holds only `elgar://plan/<id>`; the doc lives off-repo. Decision
records carry counts/labels + a PII-guarded reason — never holdings or hard PII.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from app.modules.flow.flow_decision_schema import DecisionRecord
from app.modules.plans import elgar_bridge

_COLLECTION = "decisions"
_JSON = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def decision_id(edge_id: str, decided_at: str) -> str:
    return f"{edge_id}-{decided_at.replace(':', '').replace('-', '')[:15]}"


def _doc(rec: DecisionRecord) -> str:
    return (
        f"---\nedge: {rec.edge_id}\ndecision: {rec.decision}\ndecided_at: {rec.decided_at}\n"
        f"source: orff-flow\n---\n# {rec.decision.upper()} — {rec.edge_id}\n\n"
        f"> {rec.thesis}\n\n```json\n{rec.model_dump_json(indent=2)}\n```\n"
    )


async def save(rec: DecisionRecord) -> str:
    """Write the decision; returns its elgar ref. Raises on an unreachable/invalid store."""
    entry_id = decision_id(rec.edge_id, rec.decided_at or datetime.now(UTC).isoformat())
    return await elgar_bridge.save(
        entry_id, _doc(rec), message=f"orff: decision {entry_id}", collection=_COLLECTION
    )


async def latest(edge_id: str) -> DecisionRecord | None:
    """The most recent persisted decision for an edge (None when none / store unreachable)."""
    docs = await elgar_bridge.list_docs(prefix=edge_id, collection=_COLLECTION)
    if not docs:
        return None
    content = await elgar_bridge.get(sorted(d["id"] for d in docs)[-1], collection=_COLLECTION)
    m = _JSON.search(content or "")
    return DecisionRecord.model_validate_json(m.group(1)) if m else None
