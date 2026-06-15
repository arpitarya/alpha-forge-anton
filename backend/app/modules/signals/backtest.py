"""Phase 5 backtest (§10.5) — replay the active strategy.config over history.

Composes the two halves of the live engine into round-trips: **enter** when the
screener fires (`screen_one`), **exit** when the ruleset says SELL (`evaluate`).
Per-symbol, independent, fixed equal notional — this measures the per-trade *edge
after costs*, the go/no-go before sizing up; it is not a capital/sizing portfolio
sim. Quote source is injectable so the probe replays a fixture window offline. The
`just backtest` CLI (fetch real history + print the report) lives in
`backtest_cli.py` to keep this engine pure.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date

from app.modules.signals.backtest_data import BTSeries, load_series
from app.modules.signals.backtest_metrics import build_report
from app.modules.signals.backtest_schema import BacktestConfig, BacktestReport
from app.modules.signals.indicators import compute
from app.modules.signals.quote_source import OHLCV
from app.modules.signals.screener_rules import screen_one
from app.modules.signals.signal_rules import HoldingFacts, evaluate
from app.modules.signals.signal_schema import Action, RealizedTrade
from app.modules.signals.strategy_config import StrategyConfig, load_config
from app.modules.signals.universe import resolve_universe

SeriesFn = Callable[[str, int, str | None], Awaitable[BTSeries | None]]


def _window(o: OHLCV, i: int) -> OHLCV:
    return OHLCV(high=o.high[: i + 1], low=o.low[: i + 1], close=o.close[: i + 1],
                 volume=o.volume[: i + 1])


def _close(
    symbol: str, pos: dict, qty: int, price: float, dates: list[str], i: int
) -> RealizedTrade:
    return RealizedTrade(
        symbol=symbol, qty=qty, buy_price=pos["price"], sell_price=price,
        buy_date=date.fromisoformat(dates[pos["i"]]), sell_date=date.fromisoformat(dates[i]),
    )


def simulate_symbol(
    symbol: str, s: BTSeries, cfg: StrategyConfig, bt: BacktestConfig
) -> list[RealizedTrade]:
    o, dates, n = s.ohlcv, s.dates, len(s.ohlcv.close)
    pos: dict | None = None
    trades: list[RealizedTrade] = []
    for i in range(bt.step_days, n, bt.step_days):
        ind = compute(_window(o, i))
        if ind is None:
            continue
        close = o.close[i]
        if pos is None:
            qty = int(bt.notional_inr // close)
            if qty >= 1 and screen_one(symbol, ind, cfg) is not None:
                pos = {"i": i, "price": close, "qty": qty, "trimmed": False}
            continue
        facts = HoldingFacts(symbol=symbol, avg_price=pos["price"], weight_pct=0.0, covered=True,
                             pnl_pct=(close - pos["price"]) / pos["price"] * 100)
        v = evaluate(facts, ind, cfg)
        if v.action is Action.SELL:
            trades.append(_close(symbol, pos, pos["qty"], close, dates, i))
            pos = None
        elif v.action is Action.TRIM and cfg.trim_rule.mode == "trim_half" and not pos["trimmed"]:
            if (half := pos["qty"] // 2) >= 1:
                trades.append(_close(symbol, pos, half, close, dates, i))
                pos["qty"], pos["trimmed"] = pos["qty"] - half, True
    if pos is not None:  # mark-to-close any still-open position at the final bar
        trades.append(_close(symbol, pos, pos["qty"], o.close[-1], dates, n - 1))
    return trades


async def run_backtest(
    cfg: StrategyConfig | None = None, bt: BacktestConfig | None = None,
    series_fn: SeriesFn = load_series, universe: list[str] | None = None,
) -> BacktestReport:
    cfg, bt = cfg or load_config(), bt or BacktestConfig()
    syms = universe if universe is not None else resolve_universe(cfg)
    trades: list[RealizedTrade] = []
    spans: list[str] = []
    for sym in syms:
        if (s := await series_fn(sym, bt.years, None)) is None or not s.dates:
            continue
        spans += [s.dates[0], s.dates[-1]]
        trades += simulate_symbol(sym, s, cfg, bt)
    report = build_report(trades, cfg.costs)
    period = f"{min(spans)}..{max(spans)}" if spans else ""
    return report.model_copy(update={"config_hash": cfg.hash(), "period": period,
                                     "universe_size": len(syms)})
