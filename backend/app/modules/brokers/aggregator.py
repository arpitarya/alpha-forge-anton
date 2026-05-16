"""Holdings aggregator — read-only roll-up over registered BrokerSource caches.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.modules.brokers.aggregator_types import (
    DEFAULT_TARGETS,
    AllocationSlice,
    RebalanceDrift,
    RebalanceSuggestion,
    TreemapCell,
)
from app.modules.brokers.base import AssetClass, Holding
from app.modules.brokers.fx import to_inr
from app.modules.brokers.registry import SOURCES
from app.modules.brokers.treemap_helper import squarify


def _inr_value(h: Holding) -> float:
    return to_inr(h.current_value, h.currency)


def _inr_invested(h: Holding) -> float:
    return to_inr(h.invested, h.currency)


class HoldingsAggregator:
    def __init__(self, targets: dict[AssetClass, float] | None = None) -> None:
        self.targets = targets or DEFAULT_TARGETS

    def all_holdings(self, source: str | None = None) -> list[Holding]:
        if source:
            return list(SOURCES[source].cached) if source in SOURCES else []
        merged: list[Holding] = []
        for s in SOURCES.values():
            merged.extend(s.cached)
        return merged

    def totals(self, source: str | None = None) -> dict[str, float]:
        h = self.all_holdings(source)
        invested = sum(_inr_invested(x) for x in h)
        current = sum(_inr_value(x) for x in h)
        pnl = current - invested
        # Today's INR P&L: ∑ (day_change_pct/100 × INR-normalised current_value).
        # Brokers that don't fill day_change_pct contribute 0.
        day_pnl = sum(_inr_value(x) * (x.day_change_pct / 100.0) for x in h)
        day_pnl_pct = (day_pnl / current * 100) if current else 0.0
        up = sum(1 for x in h if x.day_change_pct > 0)
        dn = sum(1 for x in h if x.day_change_pct < 0)
        return {
            "invested": round(invested, 2),
            "current_value": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round((pnl / invested * 100) if invested else 0.0, 2),
            "day_pnl": round(day_pnl, 2),
            "day_pnl_pct": round(day_pnl_pct, 2),
            "day_up": up,
            "day_dn": dn,
            "count": len(h),
        }

    def allocation(self, source: str | None = None) -> list[AllocationSlice]:
        h = self.all_holdings(source)
        total = sum(_inr_value(x) for x in h) or 1.0
        buckets: dict[AssetClass, float] = {}
        for x in h:
            buckets[x.asset_class] = buckets.get(x.asset_class, 0.0) + _inr_value(x)
        return [
            AllocationSlice(
                asset_class=c, value=round(v, 2), pct=round(v / total * 100, 2)
            )
            for c, v in sorted(buckets.items(), key=lambda kv: -kv[1])
        ]

    def treemap(self, source: str | None = None, max_cells: int = 24) -> list[TreemapCell]:
        # Sort and proportion the treemap in INR-normalised values so USD-priced
        # holdings (e.g. NVDA from IndMoney) sit alongside INR holdings correctly.
        h = sorted(self.all_holdings(source), key=lambda x: -_inr_value(x))[:max_cells]
        inr_values = [_inr_value(x) for x in h]
        total = sum(inr_values) or 1.0
        rects = squarify([v / total for v in inr_values], 0, 0, 1, 1)
        cells: list[TreemapCell] = []
        named_classes = (AssetClass.BOND, AssetClass.GOLD)
        for hold, v_inr, (lx, ly, lw, lh) in zip(h, inr_values, rects, strict=False):
            sub = (
                f"{hold.asset_class.value} · ₹{round(v_inr):,}"
                if v_inr
                else hold.asset_class.value
            )
            # Bonds/gold have cryptic scripCodes — prefer the human name when available.
            label = hold.name if (hold.name and hold.asset_class in named_classes) else hold.symbol
            cells.append(
                TreemapCell(
                    symbol=label, sublabel=sub,
                    value=v_inr,
                    pct=round(v_inr / total * 100, 2),
                    pnl=to_inr(hold.pnl, hold.currency), pnl_pct=hold.pnl_pct,
                    asset_class=hold.asset_class,
                    left_pct=round(lx * 100, 4), top_pct=round(ly * 100, 4),
                    width_pct=round(lw * 100, 4), height_pct=round(lh * 100, 4),
                )
            )
        return cells

    def rebalance(self) -> tuple[list[RebalanceDrift], list[RebalanceSuggestion]]:
        alloc = {a.asset_class: a.pct for a in self.allocation()}
        drift = [
            RebalanceDrift(
                asset_class=cls, target_pct=target,
                actual_pct=round(alloc.get(cls, 0.0), 2),
                drift_pct=round(alloc.get(cls, 0.0) - target, 2),
            )
            for cls, target in self.targets.items()
        ]
        suggestions: list[RebalanceSuggestion] = []
        for d in drift:
            if d.drift_pct > 5:
                suggestions.append(RebalanceSuggestion(
                    action=f"Trim {d.asset_class.value} ~{d.drift_pct:.0f}%"))
            elif d.drift_pct < -5:
                suggestions.append(RebalanceSuggestion(
                    action=f"Add {d.asset_class.value} ~{abs(d.drift_pct):.0f}%"))
        return drift, suggestions
