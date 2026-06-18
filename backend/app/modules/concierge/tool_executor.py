"""Dispatch tool calls — reads return data, mutating tools return confirm cards.

`execute_read` is async (calls services); `build_confirm` is sync and pure
(no I/O, never writes). The confirm-card `apply.path` is the HTTP endpoint
the frontend calls after the user taps Confirm.
See docs/orff-tool-calling.handoff.md.
"""
from __future__ import annotations

from app.modules.concierge.tool_registry import MUTATING_TOOLS


async def execute_read(name: str, args: dict) -> dict:
    """Dispatch to the matching service; raise ValueError on unknown name."""
    match name:
        case "get_plan":
            from app.modules.plans.plan_loader import load_plan
            return load_plan(args.get("plan_id", "core-allocation")).model_dump(mode="json")
        case "get_drift":
            from app.modules.plans.plan_drift import drift_for_plan
            plan, drifts = drift_for_plan(args.get("plan_id", "core-allocation"))
            return {"plan_id": plan.id, "drifts": [d.model_dump() for d in drifts]}
        case "review_holdings":
            from app.modules.signals.review_service import build_review
            plan, diff = await build_review()
            return {**plan.model_dump(mode="json"), "diff": diff.model_dump(mode="json")}
        case "screen_candidates":
            from app.modules.signals.screen_service import build_screen
            result = await build_screen(theme=args.get("theme"), limit=args.get("limit"))
            return result.model_dump(mode="json")
        case "get_strategy":
            from app.modules.signals.strategy_config import load_config
            return load_config().model_dump(mode="json")
        case "latest_action_plan":
            from app.modules.brokers.aggregator import HoldingsAggregator
            from app.modules.signals import plan_diff, plan_store
            saved = await plan_store.latest()
            if not saved:
                return {"plan": None, "diff": None}
            holdings = HoldingsAggregator().all_holdings()
            return {"plan": saved.model_dump(mode="json"),
                    "diff": plan_diff.diff(holdings, saved).model_dump(mode="json")}
        case "get_objective":
            from app.modules.signals.objective_config import load_objective
            obj = load_objective()
            return obj.model_dump(mode="json") | {"active_target": obj.active_target()}
        case _:
            raise ValueError(f"unknown read tool: {name!r}")


def build_confirm(name: str, args: dict) -> dict:
    """Return an ApprovalCard payload for a mutating tool. Sync, pure, no I/O."""
    if name not in MUTATING_TOOLS:
        raise ValueError(f"not a mutating tool: {name!r}")
    match name:
        case "set_strategy_knob":
            from app.modules.signals.strategy_tuning import propose
            return propose(args["knob"], args["value"])
        case "edit_exclusion_list":
            sym, act = args["symbol"].upper(), args["action"]
            verb, prep = ("Add", "to") if act == "add" else ("Remove", "from")
            return {
                "id": f"exclusion-{act}-{sym.lower()}",
                "action": f"{verb} {sym} {prep} never-buy list",
                "summary": f"{'Block' if act == 'add' else 'Unblock'} {sym} in hard-exclusion-list.",
                "steps": ["Read current list", f"{'Add' if act == 'add' else 'Remove'} {sym}", "Commit"],
                "apply": {"path": "/api/v1/concierge/exclusion", "body": {act: sym}},
            }
        case "update_context":
            note = args["note"]
            preview = note[:80] + ("…" if len(note) > 80 else "")
            return {
                "id": "context-append",
                "action": "Append to standing context",
                "summary": f"Add this note to your Orff context: “{preview}”",
                "steps": ["Read orff-context", "Append note + date-stamp", "Commit"],
                "apply": {"path": "/api/v1/concierge/memory/append", "body": {"note": note}},
            }
        case "save_action_plan":
            return {
                "id": "save-action-plan",
                "action": "Save ActionPlan to ledger",
                "summary": "Persist the current review plan to the elgar actions/ ledger.",
                "steps": ["Build ActionPlan from holdings", "Save to elgar actions/<date>", "Commit"],
                "apply": {"path": "/api/v1/signals/plan", "body": {}},
            }
        case "set_objective":
            changes = ", ".join(f"{k}={v}" for k, v in args.items())
            return {
                "id": "set-objective",
                "action": f"Update objective ({changes})",
                "summary": "Write new north-star target to elgar strategy/objective.md.",
                "steps": ["Validate Objective schema", "Merge into elgar strategy/objective.md", "Commit"],
                "apply": {"path": "/api/v1/signals/objective", "body": args},
            }
        case _:
            raise ValueError(f"unhandled mutating tool: {name!r}")
