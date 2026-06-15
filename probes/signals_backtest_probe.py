"""Signals backtest probe — Phase 5 acceptance (standalone, offline).

Replays the engine over a *synthetic* multi-year fixture window (no yfinance, no
network): an uptrend that fires a screener entry and rides to a mark-to-close win,
and an uptrend→crash that fires an entry then a SELL exit at a loss. Asserts the
report is **byte-identical across two runs** (determinism), that round-trips close
(both exit paths exercised), and — the point of Phase 5 — that a losing trade set
makes `positive_expectancy=False` so a config without an edge is obvious.

Run:  just probe signals-backtest   |   uv run python probes/signals_backtest_probe.py
"""

from __future__ import annotations

import asyncio
import math
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.signals.backtest import run_backtest
from app.modules.signals.backtest_data import BTSeries
from app.modules.signals.backtest_metrics import build_report
from app.modules.signals.backtest_schema import BacktestConfig
from app.modules.signals.quote_source import OHLCV
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg, StrategyConfig

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _bt(closes: list[float]) -> BTSeries:
    vols = [2000.0 if t % 5 == 0 else 1000.0 for t in range(len(closes))]
    o = OHLCV(high=[c * 1.01 for c in closes], low=[c * 0.99 for c in closes],
              close=closes, volume=vols)
    d0 = date(2023, 1, 2)
    return BTSeries(dates=[(d0 + timedelta(days=t)).isoformat() for t in range(len(closes))], ohlcv=o)


def _uptrend(n: int) -> list[float]:
    # steady drift with a proportional oscillation that keeps RSI in the 50–70 entry band
    return [100.0 * (1 + 0.004 * t) * (1 + 0.02 * math.sin(t / 4.0)) for t in range(n)]


_WIN = _uptrend(400)  # rises throughout → entry fires, mark-to-close win
_CRASH = _uptrend(260) + [_uptrend(260)[-1] * (1 - 0.012 * k) for k in range(1, 120)]  # entry then SELL
_SERIES = {"WINNER": _bt(_WIN), "CRASHER": _bt(_CRASH)}


async def _series_fn(symbol: str, years: int, exchange: str | None) -> BTSeries | None:
    return _SERIES.get(symbol)


def _t(buy: float, sell: float) -> RealizedTrade:
    return RealizedTrade(symbol="L", qty=10, buy_price=buy, sell_price=sell,
                         buy_date=date(2024, 1, 1), sell_date=date(2024, 3, 1))


async def _run() -> None:
    cfg, bt = StrategyConfig(), BacktestConfig()
    uni = ["CRASHER", "WINNER"]
    r1 = await run_backtest(cfg=cfg, bt=bt, series_fn=_series_fn, universe=uni)
    r2 = await run_backtest(cfg=cfg, bt=bt, series_fn=_series_fn, universe=uni)

    check("report is byte-identical across two runs", r1.model_dump_json() == r2.model_dump_json())
    check("round-trips closed (entry+exit paths run)", r1.trades >= 2, f"{r1.trades} trades")
    check("config hash + period stamped", bool(r1.config_hash) and bool(r1.period))
    check("metrics populated", r1.win_rate >= 0 and r1.profit_factor >= 0)

    losers = build_report([_t(100, 80), _t(100, 70), _t(100, 60)], CostsCfg())
    winners = build_report([_t(100, 150), _t(100, 140), _t(100, 130)], CostsCfg())
    check("a losing trade set → positive_expectancy=False (bad config is obvious)",
          losers.positive_expectancy is False and losers.net < 0)
    check("a winning trade set → positive_expectancy=True", winners.positive_expectancy is True)
    check("max drawdown is non-negative", r1.max_drawdown >= 0)

    print(f"\n── Backtest ({r1.period}, {r1.universe_size} symbols, {r1.trades} trades)")
    print(f"  win-rate {r1.win_rate:.0%}  net ₹{r1.net:,.0f}  "
          f"expectancy {r1.expectancy_pct:+.2f}%  maxDD ₹{r1.max_drawdown:,.0f}")
    print(f"  verdict: {'positive' if r1.positive_expectancy else 'NOT positive'} after costs")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ signals backtest FAILED" if _fail else "✅ signals backtest is deterministic"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
