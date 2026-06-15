"""Signals review probe — Phase 1 determinism + coverage check (standalone, offline).

Builds a fixture holdings set + synthetic OHLCV (no yfinance, no network), runs
`build_action_plan` twice, and asserts the two `ActionPlan`s are **byte-identical**
(the Phase 1 contract: same holdings + same config ⇒ same plan). Also checks one
verdict per holding, that a US holding is HOLD "not covered", and prints the plan.

Run:  just signals-review   |   uv run python probes/signals_review_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.broker_schemas import AssetClass, Holding
from app.modules.signals.quote_source import OHLCV
from app.modules.signals.review_service import build_action_plan
from app.modules.signals.strategy_config import StrategyConfig

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _series(start: float, end: float, n: int = 80) -> OHLCV:
    closes = [start + (end - start) * i / (n - 1) for i in range(n)]
    return OHLCV(high=[c * 1.01 for c in closes], low=[c * 0.99 for c in closes],
                 close=closes, volume=[1000.0 + i for i in range(n)])


_QUOTES = {"FALLER": _series(150, 100), "RISER": _series(100, 122)}


async def _quote(symbol: str, exchange: str | None) -> OHLCV | None:
    return _QUOTES.get(symbol)


def _holding(symbol: str, pnl_pct: float, value: float, currency: str = "INR") -> Holding:
    return Holding(source="fixture", asset_class=AssetClass.EQUITY, symbol=symbol,
                   quantity=10, avg_price=100, last_price=100 * (1 + pnl_pct / 100),
                   invested=value / (1 + pnl_pct / 100), current_value=value,
                   pnl=0.0, pnl_pct=pnl_pct, currency=currency, exchange="NSE")


HOLDINGS = [
    _holding("FALLER", -8.0, 50_000),
    _holding("RISER", 12.0, 80_000),
    _holding("NVDA", 30.0, 40_000, currency="USD"),  # US -> not covered
]


async def _run() -> None:
    cfg = StrategyConfig()
    plan_a = await build_action_plan(cfg=cfg, holdings=HOLDINGS, quote=_quote)
    plan_b = await build_action_plan(cfg=cfg, holdings=HOLDINGS, quote=_quote)

    a, b = plan_a.model_dump_json(), plan_b.model_dump_json()
    check("ActionPlan is byte-identical across two runs", a == b)
    check("one verdict per holding", len(plan_a.verdicts) == len(HOLDINGS),
          f"{len(plan_a.verdicts)} vs {len(HOLDINGS)}")
    check("config hash stamped on the plan", bool(plan_a.config_hash))

    by_sym = {v.symbol: v for v in plan_a.verdicts}
    check("US holding (NVDA) -> HOLD not covered",
          by_sym["NVDA"].action.value == "hold" and "not covered" in by_sym["NVDA"].reason)
    check("verdicts are symbol-sorted (deterministic order)",
          [v.symbol for v in plan_a.verdicts] == sorted(v.symbol for v in plan_a.verdicts))

    print(f"\n── ActionPlan (config {plan_a.config_hash}, universe {plan_a.universe_mode})")
    for v in plan_a.verdicts:
        stop = f" stop {v.stop_price}" if v.stop_price is not None else ""
        print(f"  {v.action.value.upper():5} {v.symbol:8} c{v.conviction}  {v.reason}{stop}")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ signals review FAILED" if _fail else "✅ signals review is deterministic"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
