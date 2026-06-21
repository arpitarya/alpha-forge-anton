"""Round-trip cost model for the edge engine — frictions + STCG + slippage. Pure.

Single source of truth for tax/friction is the signals `CostsCfg` + `realized_pnl`
(STCG ~20%, STT, the stamp/exchange/SEBI/GST bundle) — not re-derived here. We add
one knob the live tracker doesn't model, because discovery must be honest about it:
`slippage_pct`, charged on both legs (you don't trade at the close). Short holding
periods → high turnover → these costs dominate, which is exactly the trap a real
edge has to clear. `net_pct` is per-trade net % of buy value — the discovery lens.
"""

from __future__ import annotations

from datetime import date

from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg

DEFAULT_SLIPPAGE_PCT = 0.05  # per leg, % of value — realistic for liquid NSE large/mid


def _slip(value: float, slippage_pct: float) -> float:
    return slippage_pct / 100 * value


def net_pct(
    buy_price: float,
    sell_price: float,
    qty: float,
    buy_date: date,
    sell_date: date,
    costs: CostsCfg,
    slippage_pct: float = DEFAULT_SLIPPAGE_PCT,
) -> float:
    """One round-trip → net return % after frictions, STCG, and entry+exit slippage."""
    t = RealizedTrade(
        symbol="E",
        qty=qty,
        buy_price=buy_price,
        sell_price=sell_price,
        buy_date=buy_date,
        sell_date=sell_date,
    )
    after_tax = realized_pnl([t], costs).net  # frictions + STCG (ST-loss aware)
    slip = _slip(qty * buy_price, slippage_pct) + _slip(qty * sell_price, slippage_pct)
    return (after_tax - slip) / (qty * buy_price) * 100
