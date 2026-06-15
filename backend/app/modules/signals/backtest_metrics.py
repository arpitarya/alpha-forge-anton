"""Closed round-trips → a `BacktestReport`. Pure: no I/O, no clock (§10.5).

Two cost lenses, on purpose:
  • per-trade **friction net** (brokerage+STT+friction, pre-tax) drives win-rate,
    expectancy, and the drawdown curve — the *trading edge*. STCG is a
    portfolio overlay on gains, not a per-trade win/lose signal.
  • the headline **net** is the full after-cost figure from `realized_pnl`
    (frictions + STCG with ST-loss offset) — "P&L AFTER costs".
"""

from __future__ import annotations

from app.modules.signals.backtest_schema import BacktestReport
from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg


def _friction_net(t: RealizedTrade, c: CostsCfg) -> float:
    """gross P&L minus the explicit, per-trade frictions (no tax)."""
    buy_val, sell_val = t.qty * t.buy_price, t.qty * t.sell_price
    frictions = 2 * c.brokerage_per_order_inr + (c.stt_pct + c.friction_pct) / 100 * (
        buy_val + sell_val
    )
    return (sell_val - buy_val) - frictions


def _max_drawdown(curve: list[float]) -> tuple[float, float]:
    """Deepest peak-to-trough on a cumulative-P&L curve → (₹, % of peak profit)."""
    peak = dd = dd_pct = 0.0
    for equity in curve:
        peak = max(peak, equity)
        drop = peak - equity
        if drop > dd:
            dd = drop
            dd_pct = (drop / peak * 100) if peak > 0 else 0.0
    return round(dd, 2), round(dd_pct, 2)


def build_report(trades: list[RealizedTrade], costs: CostsCfg) -> BacktestReport:
    if not trades:
        return BacktestReport(notes=["no round-trips closed in the window"])

    ordered = sorted(trades, key=lambda t: (t.sell_date, t.symbol))
    fnets = [_friction_net(t, costs) for t in ordered]
    wins = [n for n in fnets if n > 0]
    losses = [n for n in fnets if n <= 0]
    pct_returns = [_friction_net(t, costs) / (t.qty * t.buy_price) * 100 for t in ordered]

    curve, running = [], 0.0
    for n in fnets:
        running += n
        curve.append(running)
    dd, dd_pct = _max_drawdown(curve)

    gross = sum(t.qty * (t.sell_price - t.buy_price) for t in ordered)
    full = realized_pnl(ordered, costs)
    n = len(ordered)
    return BacktestReport(
        trades=n,
        wins=len(wins),
        win_rate=round(len(wins) / n, 4),
        gross=round(gross, 2),
        net=full.net,
        expectancy_inr=round(sum(fnets) / n, 2),
        expectancy_pct=round(sum(pct_returns) / n, 2),
        avg_win=round(sum(wins) / len(wins), 2) if wins else 0.0,
        avg_loss=round(sum(losses) / len(losses), 2) if losses else 0.0,
        profit_factor=round(sum(wins) / abs(sum(losses)), 2) if losses and sum(losses) else 0.0,
        max_drawdown=dd,
        max_drawdown_pct=dd_pct,
        positive_expectancy=full.net > 0 and sum(fnets) > 0,
    )
