"""Plan-aware rebalance drift — joins a committed plan with live actuals.

Bridges the **plan plane** (committed targets/bands via `plan_loader`) and the
**data plane** (live holdings via `HoldingsAggregator`) into per-class drift expressed
in *percentage points only* — no ₹, no symbols — so the result is safe to disclose to
the concierge. Band-aware: each class is judged against its own tolerance. See the Fux
`secure-holdings-plan` entry.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.plan_loader import Plan, load_plan


@dataclass
class ClassDrift:
    asset_class: str
    target_pct: float
    actual_pct: float
    drift_pct: float
    band: float
    status: str  # "ok" | "hot" (over band) | "cold" (under band)
    action: str  # "" | "trim ~Npts" | "add ~Npts"


def drift_for_plan(plan_id: str = "core-allocation") -> tuple[Plan, list[ClassDrift]]:
    """Return (plan, per-class band-aware drift) for a committed plan vs live holdings."""
    plan = load_plan(plan_id)
    agg = HoldingsAggregator(targets=plan.targets)
    rows, _ = agg.rebalance()
    out: list[ClassDrift] = []
    for r in rows:
        band = plan.band_for(r.asset_class)
        d = r.drift_pct
        if d > band:
            status, action = "hot", f"trim ~{d:.0f}pts"
        elif d < -band:
            status, action = "cold", f"add ~{abs(d):.0f}pts"
        else:
            status, action = "ok", ""
        out.append(
            ClassDrift(
                r.asset_class.value, r.target_pct, r.actual_pct, r.drift_pct, band, status, action
            )
        )
    return plan, out


def has_live_data(rows: list[ClassDrift]) -> bool:
    """True when any class shows a non-zero actual — i.e. a broker cache is populated."""
    return any(r.actual_pct for r in rows)


__all__ = ["ClassDrift", "drift_for_plan", "has_live_data"]
