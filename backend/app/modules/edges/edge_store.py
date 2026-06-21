"""Read/write the pre-registered edge doc in the elgar `edges` collection.

The edge hypothesis is money/strategy content → it lives in the private elgar store,
never this repo (the plan-store constitution). The repo holds only `elgar://edge/<id>`.
Mirrors `signals.plan_store`: one save = one git commit in the store, fenced-JSON body
parsed back on load. Reuses the best-effort `plans.elgar_bridge` subprocess. Fail-soft:
a missing/unreachable store returns None, never crashes a discovery run.
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

from app.modules.edges.edge_schema import EdgeSpec
from app.modules.plans import elgar_bridge

logger = logging.getLogger(__name__)

_COLLECTION = "edges"
_JSON = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def new_edge_id() -> str:
    return f"edge-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"


def _doc(spec: EdgeSpec) -> str:
    today = datetime.now(UTC).isoformat()
    return (
        f"---\nid: {spec.id}\ncreated: {today}\nsignal: {spec.signal}\n"
        f"status: {spec.status.value}\nsource: orff-edges\n---\n"
        f"# Edge {spec.id}\n\n> {spec.hypothesis}\n\n"
        f"```json\n{spec.model_dump_json(indent=2)}\n```\n"
    )


async def save(spec: EdgeSpec) -> str | None:
    try:
        return await elgar_bridge.save(
            spec.id, _doc(spec), message=f"orff: edge {spec.id}", collection=_COLLECTION
        )
    except Exception as e:  # best-effort — a down store never blocks discovery
        logger.warning("edge save failed: %s", e)
        return None


async def load(edge_id: str) -> EdgeSpec | None:
    try:
        content = await elgar_bridge.get(edge_id, collection=_COLLECTION)
        m = _JSON.search(content or "")
        return EdgeSpec.model_validate_json(m.group(1)) if m else None
    except Exception as e:
        logger.warning("edge load failed: %s", e)
        return None
