"""Monthly realized-P&L — gross minus EXPLICIT frictions and short-term tax (§10.4).

Pure: a list of closed round-trips + the cost knobs → a `RealizedReport`, net of
brokerage, STT, the stamp/exchange/SEBI/GST friction bundle, and STCG on
short-term gains (ST losses offset ST gains; long-term gains are untaxed here —
LTCG is a follow-up). Costs are config knobs, never hardcoded: rates change in
Finance Acts (Fux transaction-costs / capital-gains-equity). No I/O, no clock.
"""

from __future__ import annotations

from app.modules.signals.signal_schema import RealizedReport, RealizedTrade
from app.modules.signals.strategy_config import CostsCfg

_ST_MAX_DAYS = 365  # held ≤ 12 months ⇒ short-term (capital-gains-equity)


def _is_short_term(t: RealizedTrade) -> bool:
    return (t.sell_date - t.buy_date).days <= _ST_MAX_DAYS


def realized_pnl(
    trades: list[RealizedTrade], costs: CostsCfg, target: float = 0.0
) -> RealizedReport:
    gross = brokerage = stt = friction = short_term = 0.0
    for t in trades:
        buy_val, sell_val = t.qty * t.buy_price, t.qty * t.sell_price
        pnl = sell_val - buy_val
        gross += pnl
        brokerage += 2 * costs.brokerage_per_order_inr  # buy + sell legs
        stt += costs.stt_pct / 100 * (buy_val + sell_val)
        friction += costs.friction_pct / 100 * (buy_val + sell_val)
        if _is_short_term(t):
            short_term += pnl
    stcg = costs.stcg_pct / 100 * max(0.0, short_term)
    net = gross - brokerage - stt - friction - stcg
    return RealizedReport(
        gross=round(gross, 2),
        brokerage=round(brokerage, 2),
        stt=round(stt, 2),
        friction=round(friction, 2),
        stcg=round(stcg, 2),
        net=round(net, 2),
        short_term_gain=round(short_term, 2),
        target=round(target, 2),
        vs_target=round(net - target, 2),
        trades=len(trades),
    )
