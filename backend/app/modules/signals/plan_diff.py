"""Diff today's holdings against the snapshot inside the last saved plan (§7).

Pure. Surfaces what changed since the plan was made — positions exited, new buys,
stops that fired, and **un-acted verdicts** (the last plan said SELL/TRIM/ADD but
the holding is materially unchanged) — so Orff reasons from the prior plan, not
blind. No store/None plan ⇒ an empty diff (fresh start).
"""

from __future__ import annotations

from app.modules.brokers.broker_schemas import Holding
from app.modules.signals.signal_schema import Action, PlanDiff, SavedPlan

_QTY_EPS = 0.01  # relative qty change below this counts as "unchanged"
_ACTIONABLE = {Action.SELL, Action.TRIM, Action.ADD}


def diff(holdings: list[Holding], plan: SavedPlan | None) -> PlanDiff:
    if plan is None:
        return PlanDiff()
    today = {h.symbol: h for h in holdings}
    snap = {s.symbol: s for s in plan.snapshot}
    stops = {v.symbol: v.stop_price for v in plan.verdicts if v.stop_price is not None}

    stops_fired = sorted(
        sym for sym, h in today.items() if sym in stops and h.last_price < stops[sym]
    )
    unacted: list[str] = []
    for v in plan.verdicts:
        if v.action not in _ACTIONABLE:
            continue
        h, s = today.get(v.symbol), snap.get(v.symbol)
        if h is None or s is None or not s.qty:
            continue
        if abs(h.quantity - s.qty) / s.qty < _QTY_EPS:
            unacted.append(f"{v.symbol}: {v.action.value.upper()} last plan, unchanged")

    return PlanDiff(
        exited=sorted(s for s in snap if s not in today),
        new_positions=sorted(s for s in today if s not in snap),
        stops_fired=stops_fired,
        unacted=sorted(unacted),
    )
