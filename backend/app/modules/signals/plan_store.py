"""Read/write the elgar `actions/` plan ledger — one saved plan = one git commit.

Each saved ActionPlan embeds the holdings snapshot + verdicts + stop prices it was
based on, so `plan_diff` can later compare today's holdings to the plan that was in
force. Reuses `plans.elgar_bridge` (the `--dir actions` collection). Best-effort:
a missing/unreachable store returns None and the chat degrades to a fresh plan,
never blocks (handoff §7).
"""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

from app.modules.brokers.broker_schemas import Holding
from app.modules.brokers.fx import to_inr
from app.modules.plans import elgar_bridge
from app.modules.signals.signal_schema import ActionPlan, HoldingSnap, SavedPlan

logger = logging.getLogger(__name__)

_COLLECTION = "actions"
_JSON = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def new_plan_id() -> str:
    return f"plan-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"


def to_saved(plan: ActionPlan, holdings: list[Holding], plan_id: str) -> SavedPlan:
    snap = [
        HoldingSnap(
            symbol=h.symbol,
            qty=h.quantity,
            value=round(to_inr(h.current_value, h.currency), 2),
            price=h.last_price,
        )
        for h in holdings
    ]
    return SavedPlan(
        plan_id=plan_id, config_hash=plan.config_hash, snapshot=snap, verdicts=plan.verdicts
    )


def _doc(plan: SavedPlan) -> str:
    today = datetime.now(UTC).isoformat()
    return (
        f"---\nid: {plan.plan_id}\ncreated: {today}\nconfig: {plan.config_hash}\n"
        f"source: orff-signals\n---\n# Action plan {plan.plan_id}\n\n"
        f"```json\n{plan.model_dump_json(indent=2)}\n```\n"
    )


async def save(plan: SavedPlan) -> str | None:
    try:
        return await elgar_bridge.save(
            plan.plan_id,
            _doc(plan),
            message=f"orff: action plan {plan.plan_id}",
            collection=_COLLECTION,
        )
    except Exception as e:  # best-effort — a down store never blocks the chat
        logger.warning("actions save failed: %s", e)
        return None


async def latest() -> SavedPlan | None:
    try:
        docs = await elgar_bridge.list_docs(collection=_COLLECTION)
        if not docs:
            return None
        newest = max(docs, key=lambda d: d.get("id", ""))
        content = await elgar_bridge.get(newest["id"], collection=_COLLECTION)
        m = _JSON.search(content or "")
        return SavedPlan.model_validate_json(m.group(1)) if m else None
    except Exception as e:
        logger.warning("actions latest failed: %s", e)
        return None
