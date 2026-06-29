"""Live-stage logic — prepare the exact orders and reconcile the human's fills.

NEVER places a broker order and NEVER auto-executes (the hard invariant). `build_plan` turns an
approved size into a copy-only order list + the staged -12 / -20 guard + an execution checklist;
`reconcile` reads back the human-entered fills to compute true P&L, slippage vs the plan, and the
guard state. Pure, deterministic, no I/O, no broker call — the human places everything.
"""

from __future__ import annotations

from app.modules.flow.flow_live_schema import (
    Fill,
    GuardState,
    OrderKind,
    OrderPlan,
    OrderSide,
    PreparedOrder,
    ReconcileResult,
)

SOFT_PCT = -12.0  # mandate drawdown guard — de-risk
HARD_PCT = -20.0  # mandate drawdown guard — flatten


def build_plan(edge_id: str, thesis: str, notional: float) -> OrderPlan:
    """The exact orders for an approved edge — entry + staged guards + checklist. Copy-only."""
    orders = [
        PreparedOrder(
            side=OrderSide.BUY,
            kind=OrderKind.ENTRY,
            notional=round(notional, 2),
            label=f"BUY entry — Rs {notional:,.0f} across the edge basket, at/under limit",
        ),
        PreparedOrder(
            side=OrderSide.SELL,
            kind=OrderKind.GUARD,
            level_pct=SOFT_PCT,
            label="De-risk at -12% — trim and pause new deployment",
        ),
        PreparedOrder(
            side=OrderSide.SELL,
            kind=OrderKind.GUARD,
            level_pct=HARD_PCT,
            label="Flatten at -20% — full stop, sell the position",
        ),
    ]
    checklist = [
        "Copy each order into YOUR broker and place it — Orff never places an order.",
        f"Open the entry only up to Rs {notional:,.0f}; equal-weight the basket names.",
        "Set the -12% de-risk and -20% hard stop the moment the entry fills.",
        "Record your actual fills below to reconcile true P&L vs this plan.",
    ]
    return OrderPlan(
        edge_id=edge_id,
        thesis=thesis,
        notional=round(notional, 2),
        orders=orders,
        checklist=checklist,
    )


def _guard(pnl_pct: float) -> tuple[GuardState, str]:
    if pnl_pct <= HARD_PCT:
        return GuardState.HARD, f"HARD GUARD breached ({pnl_pct:.1f}% <= -20%) — flatten and review"
    if pnl_pct <= SOFT_PCT:
        return GuardState.SOFT, f"soft guard ({pnl_pct:.1f}% <= -12%) — de-risk, no new deployment"
    return GuardState.OK, f"within guard ({pnl_pct:.1f}%)"


def reconcile(notional: float, fills: list[Fill]) -> ReconcileResult:
    """True P&L from the human's fills — invested vs current, slippage vs plan, guard state."""
    invested = sum(f.qty * f.buy_price + f.fees for f in fills)
    current = sum(f.qty * (f.last_price or f.buy_price) for f in fills)
    pnl = current - invested
    pnl_pct = round(pnl / invested * 100, 2) if invested else 0.0
    state, msg = _guard(pnl_pct)
    return ReconcileResult(
        invested=round(invested, 2),
        current_value=round(current, 2),
        pnl=round(pnl, 2),
        pnl_pct=pnl_pct,
        slippage=round(invested - notional, 2),
        guard=state,
        notes=[msg, "Orff never placed these orders — you did; this is read-back only"],
    )
