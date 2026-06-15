"""Signals re-plan probe — Phase 3 acceptance (standalone, offline).

Simulates a saved plan, then runs `build_review` against **changed** holdings and
asserts the diff is reported (un-acted verdict + new position + exits + a fired
stop), deterministically across two runs. `plan_store.latest` is stubbed so the
loop runs without an elgar store (it is best-effort in production).

Run:  just probe signals-replan
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.broker_schemas import AssetClass, Holding
from app.modules.signals import plan_store, review_service
from app.modules.signals.signal_schema import Action, HoldingSnap, SavedPlan, Verdict

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _h(symbol: str, qty: float, price: float = 100.0) -> Holding:
    return Holding(source="fix", asset_class=AssetClass.EQUITY, symbol=symbol, quantity=qty,
                   avg_price=100, last_price=price, invested=1000, current_value=qty * price,
                   pnl=0, pnl_pct=0, currency="INR", exchange="NSE")


def _snap(symbol: str, qty: float, price: float = 100.0) -> HoldingSnap:
    return HoldingSnap(symbol=symbol, qty=qty, value=qty * price, price=price)


_SAVED = SavedPlan(
    plan_id="plan-1", config_hash="x",
    snapshot=[_snap("HAL", 10), _snap("BEL", 5), _snap("OLD", 3), _snap("DROP", 8)],
    verdicts=[
        Verdict(symbol="HAL", action=Action.TRIM, reason="+60%", stop_price=90),
        Verdict(symbol="OLD", action=Action.SELL, reason="stop", stop_price=120),
        Verdict(symbol="DROP", action=Action.HOLD, reason="hold", stop_price=150),
    ],
)
# HAL unchanged (unacted TRIM), DROP < its stop (fired), NEW added, BEL+OLD exited.
_TODAY = [_h("HAL", 10), _h("DROP", 8, price=100.0), _h("NEW", 7)]


async def _noquote(symbol: str, exchange: str | None):  # offline: every symbol -> HOLD "no data"
    return None


async def _run() -> None:
    async def fake_latest() -> SavedPlan:
        return _SAVED

    plan_store.latest = fake_latest  # stub the elgar store

    _, d1 = await review_service.build_review(holdings=_TODAY, quote=_noquote)
    _, d2 = await review_service.build_review(holdings=_TODAY, quote=_noquote)

    check("diff is deterministic across two /review runs", d1.model_dump_json() == d2.model_dump_json())
    check("exited positions reported", d1.exited == ["BEL", "OLD"], str(d1.exited))
    check("new position reported", d1.new_positions == ["NEW"], str(d1.new_positions))
    check("fired stop reported", d1.stops_fired == ["DROP"], str(d1.stops_fired))
    check("un-acted verdict reported", d1.unacted == ["HAL: TRIM last plan, unchanged"], str(d1.unacted))

    # No store ⇒ empty diff (fresh start), never an error
    async def none_latest():
        return None

    plan_store.latest = none_latest
    _, d3 = await review_service.build_review(holdings=_TODAY, quote=_noquote)
    check("missing store degrades to an empty diff", d3 == d3.__class__(), d3.model_dump_json())

    print("\n── Re-plan diff")
    print(f"  exited={d1.exited}  new={d1.new_positions}  stops_fired={d1.stops_fired}")
    print(f"  unacted={d1.unacted}")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ re-plan loop FAILED" if _fail else "✅ re-plan loop reports the diff"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
