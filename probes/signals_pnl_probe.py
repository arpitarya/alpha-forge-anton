"""Signals net-P&L probe — Phase 4 acceptance (standalone, offline).

Feeds a fixed set of closed round-trips (short-term gain, short-term loss, a
long-term gain) through `realized_pnl` and asserts the tracker nets the costs
correctly — brokerage + STT + friction + STCG (ST-loss-offset, LT untaxed) — to a
hand-computed total, deterministically. This is the §10.4 "Done" check.

Run:  just probe signals-pnl
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.signals.pnl_tracker import realized_pnl
from app.modules.signals.signal_schema import RealizedTrade
from app.modules.signals.strategy_config import CostsCfg

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _t(buy: float, sell: float, qty: float, days: int) -> RealizedTrade:
    return RealizedTrade(symbol="X", qty=qty, buy_price=buy, sell_price=sell,
                         buy_date=date(2026, 1, 1), sell_date=date(2026, 1, 1) + timedelta(days=days))


# ST +500, ST -300, LT +300 (untaxed). Turnover legs: 2500 + 1700 + 2300 = 6500.
_TRADES = [_t(100, 150, 10, 59), _t(100, 70, 10, 59), _t(200, 260, 5, 400)]
_COSTS = CostsCfg()  # brokerage 20/order, stt 0.1%, friction 0.03%, stcg 20%
_TARGET = 250.0


def main() -> int:
    r1 = realized_pnl(_TRADES, _COSTS, target=_TARGET)
    r2 = realized_pnl(_TRADES, _COSTS, target=_TARGET)

    check("deterministic across two runs", r1.model_dump_json() == r2.model_dump_json())
    check("gross = 500 (+500 −300 +300)", r1.gross == 500.0, str(r1.gross))
    check("brokerage = 120 (3 trades × 2 × ₹20)", r1.brokerage == 120.0, str(r1.brokerage))
    check("STT = 6.5 (0.1% × 6500 turnover)", r1.stt == 6.5, str(r1.stt))
    check("friction = 1.95 (0.03% × 6500)", r1.friction == 1.95, str(r1.friction))
    check("short-term gain = 200 (ST loss offsets ST gain)", r1.short_term_gain == 200.0,
          str(r1.short_term_gain))
    check("STCG = 40 (20% × 200; LT untaxed)", r1.stcg == 40.0, str(r1.stcg))
    check("net = 331.55 (gross − all costs)", r1.net == 331.55, str(r1.net))
    check("vs_target = 81.55 (net − 250)", r1.vs_target == 81.55, str(r1.vs_target))

    print(f"\n── RealizedReport ({r1.trades} trades)")
    print(f"  gross {r1.gross}  − brokerage {r1.brokerage}  − STT {r1.stt}  "
          f"− friction {r1.friction}  − STCG {r1.stcg}")
    print(f"  net {r1.net}  vs target {r1.target} → {r1.vs_target:+}")

    print("\n" + ("❌ net-P&L FAILED" if _fail else "✅ net-P&L tracker nets costs correctly"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
