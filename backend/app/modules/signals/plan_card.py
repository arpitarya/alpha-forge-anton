"""Deterministic plan card — an ActionPlan + diff rendered as a Fux-whitelisted UISpec.

Built server-side from the engine's own numbers (no LLM), so the card never mangles
a figure. Emitted as a `{spec}` SSE event on a /review turn and drawn by the existing
SpecHost/DynamicRenderer path (Card + Text + DataTable are already whitelisted).
"""

from __future__ import annotations

import logging

from app.modules.signals.review_service import build_review
from app.modules.signals.signal_schema import ActionPlan, PlanDiff

logger = logging.getLogger(__name__)

_COLUMNS = [
    {"key": "action", "label": "Verdict"},
    {"key": "symbol", "label": "Symbol"},
    {"key": "stop", "label": "Stop", "align": "right"},
    {"key": "target", "label": "Target", "align": "right"},
    {"key": "changed", "label": "Δ since last"},
]


def is_review(prompt: str) -> bool:
    return "review" in (prompt or "").lower()


def _changed_map(diff: PlanDiff) -> dict[str, str]:
    m: dict[str, str] = {}
    for s in diff.new_positions:
        m[s] = "new"
    for s in diff.stops_fired:
        m[s] = "stop fired"
    for u in diff.unacted:
        m.setdefault(u.split(":")[0], "unacted")
    return m


def _rows(plan: ActionPlan, diff: PlanDiff) -> list[dict]:
    changed = _changed_map(diff)
    return [
        {
            "action": v.action.value.upper(),
            "symbol": v.symbol,
            "stop": v.stop_price if v.stop_price is not None else "—",
            "target": v.target_price if v.target_price is not None else "—",
            "changed": changed.get(v.symbol, ""),
        }
        for v in plan.verdicts
    ]


def build_spec(plan: ActionPlan, diff: PlanDiff) -> dict:
    title = f"Action plan — {len(plan.verdicts)} holdings (config {plan.config_hash})"
    return {
        "component": "Card",
        "children": [
            {"component": "Text", "props": {"size": "headline"}, "children": [{"text": title}]},
            {
                "component": "DataTable",
                "props": {"columns": _COLUMNS, "rows": _rows(plan, diff), "maxRows": 60},
            },
        ],
    }


async def review_spec(prompt: str) -> dict | None:
    """`{spec, spec_provider}` for a /review turn, else None. Best-effort."""
    if not is_review(prompt):
        return None
    try:
        plan, diff = await build_review()
    except Exception as e:  # best-effort — a failed card never breaks the answer
        logger.debug("plan card skipped: %s", e)
        return None
    return {"spec": build_spec(plan, diff), "spec_provider": "signals"}
