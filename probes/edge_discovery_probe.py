"""Edge-discovery probe — gates 1-2 + pre-registration discipline (standalone, offline).

Replays the discovery loop over *synthetic* fixtures (no yfinance, no network, no elgar):
  • a genuine momentum edge on a steady uptrend → clears BOTH gates,
  • a deliberately overfit weekday edge → passes gate 1 but is KILLED at gate 2,
  • a hypothesis dated AFTER the run → refused by the pre-registration gate (no result),
  • gate 1 is byte-identical across two runs (the determinism contract).
Journaling is disabled (journal=False) so the probe touches no store.

Run:  just probe edge-discovery   |   uv run python probes/edge_discovery_probe.py
"""

from __future__ import annotations

import asyncio
import math
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.edges.edge_backtest import OOS_FRACTION, run_gate1
from app.modules.edges.edge_data import Bars
from app.modules.edges.edge_discover import discover
from app.modules.edges.edge_register import PreRegistrationError
from app.modules.edges.edge_schema import EdgeSpec

_fail = 0
_RUN = datetime(2026, 6, 21, tzinfo=UTC)


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _dates(n: int) -> list[str]:
    return [f"2024-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)]


def _real() -> Bars:
    n = 300
    # uptrend with pullbacks → a real (small) drawdown, so the Calmar-0 guard accepts it.
    closes = [2000.0 * (1.004**i) * (1.0 + 0.04 * math.sin(i / 5.0)) for i in range(n)]
    return Bars(dates=_dates(n), close=closes)


def _overfit() -> Bars:
    n, closes = 280, [2000.0] * 280
    tail, sl = int(280 * (1 - OOS_FRACTION)), 280 // 5
    for i in range(n):
        if i + 5 >= n:
            continue
        if i >= tail and i % 7 == 0:
            closes[i + 5] = closes[i] * 1.05
        elif i < tail:
            lucky = (i // sl * 3) % 7
            if i % 7 == lucky:
                closes[i + 5] = closes[i] * 1.04
            elif i % 7 == (lucky + 2) % 7:
                closes[i + 5] = closes[i] * 0.95
    return Bars(dates=_dates(n), close=closes)


def _provider(b: Bars):
    class _P:
        async def bars(self, symbol: str, years: int) -> Bars:
            return b

    return _P()


def _spec(signal: str, pre: datetime | None = _RUN - timedelta(days=1)) -> EdgeSpec:
    return EdgeSpec(id="probe", hypothesis="h", universe=["X"], signal=signal,
                    holding_period_days=5, pre_registered_at=pre)


async def _run() -> None:
    real = await discover(_spec("momentum"), _provider(_real()), run_at=_RUN, journal=False)
    check("genuine edge clears BOTH gates", len(real) == 2 and all(g.passed for g in real),
          f"{[(g.gate, g.passed) for g in real]}")

    trap = await discover(_spec("overfit_dayofmonth"), _provider(_overfit()), run_at=_RUN, journal=False)
    check("overfit edge PASSES gate 1", trap[0].passed is True, f"g1 exp {trap[0].stats.expectancy_pct}")
    check("overfit edge is KILLED at gate 2", len(trap) == 2 and trap[1].passed is False,
          f"g2 calmar {trap[1].stats.calmar if len(trap) == 2 else 'n/a'}")

    refused = False
    try:
        await discover(_spec("momentum", pre=_RUN + timedelta(days=1)), _provider(_real()),
                       run_at=_RUN, journal=False)
    except PreRegistrationError:
        refused = True
    check("post-result hypothesis is refused (pre-registration)", refused)

    a = await run_gate1(_spec("overfit_dayofmonth"), _provider(_overfit()))
    b = await run_gate1(_spec("overfit_dayofmonth"), _provider(_overfit()))
    check("gate 1 is byte-identical across runs", a.model_dump_json() == b.model_dump_json())

    print(f"\n── REAL  g1 {real[0].stats.expectancy_pct:+.2f}%  g2 Calmar {real[1].stats.calmar}")
    print(f"── TRAP  g1 {trap[0].stats.expectancy_pct:+.2f}% (pass)  "
          f"g2 Calmar {trap[1].stats.calmar} (KILL)")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ edge discovery FAILED" if _fail else "✅ edge discovery: gates + discipline hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
