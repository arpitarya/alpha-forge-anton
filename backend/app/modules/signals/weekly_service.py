"""The weekly review job (§10.4) — the callable Cowork's scheduler triggers.

Runs the deterministic review, best-effort saves it to the elgar `actions/` ledger
(the weekly checkpoint that makes next week's diff meaningful), and emits the
actionable verdicts + any fired stops. No auto-trading — stop/target prices are
for manual GTT entry only.
"""

from __future__ import annotations

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.signals import plan_store
from app.modules.signals.review_service import build_review
from app.modules.signals.signal_schema import Action, WeeklyReview

_ACTIONABLE = {Action.SELL, Action.TRIM, Action.ADD}


async def weekly_review() -> WeeklyReview:
    holdings = HoldingsAggregator().all_holdings()
    plan, diff = await build_review(holdings=holdings)
    saved = plan_store.to_saved(plan, holdings, plan_store.new_plan_id())
    ref = await plan_store.save(saved)  # best-effort — None when the store is down
    actions = [v for v in plan.verdicts if v.action in _ACTIONABLE]
    return WeeklyReview(actions=actions, stops_fired=diff.stops_fired, saved_ref=ref)
