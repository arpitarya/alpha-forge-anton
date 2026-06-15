"""Signals screen probe — Phase 2 determinism + ranking check (standalone, offline).

Drives `build_screen` over a fixture universe and asserts the `ScreenResult` is
**byte-identical across two runs**, score-ordered, top-N capped, and that gate
failures / no-data symbols are excluded. `indicators.compute` is replaced with a
fixture map so the screen is portable (talib values on synthetic data are
version-sensitive); the real indicators path is covered by the /review probe and
the screener unit tests.

Run:  just signals-screen   |   uv run python probes/signals_screen_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.signals import screen_service
from app.modules.signals.indicators import Indicators
from app.modules.signals.quote_source import OHLCV
from app.modules.signals.strategy_config import StrategyConfig

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _ind(adx, pos, rsi, vol, close=100.0) -> Indicators:
    return Indicators(close=close, rsi14=rsi, adx14=adx, dma50=close * 0.9, dma200=close * 0.8,
                      atr14=2.0, recent_high=close, pos_52w=pos, vol_ratio=vol)


# symbol -> fixture indicators. ALFA/BETA clear every gate (ALFA scores higher);
# GAMMA fails ADX + RSI; DELTA has no quote (no-data skip).
_FIX = {
    "ALFA": _ind(adx=45, pos=0.99, rsi=60, vol=3.0, close=200),
    "BETA": _ind(adx=28, pos=0.92, rsi=58, vol=1.8, close=100),
    "GAMMA": _ind(adx=20, pos=0.95, rsi=80, vol=2.0),
}
_OHLCV = {s: OHLCV(high=[1.0], low=[1.0], close=[1.0], volume=[1.0]) for s in _FIX}
_BY_ID = {id(_OHLCV[s]): _FIX[s] for s in _FIX}
_UNIVERSE = ["ALFA", "BETA", "GAMMA", "DELTA"]  # DELTA -> no quote


async def _quote(symbol: str, exchange: str | None) -> OHLCV | None:
    return _OHLCV.get(symbol)


def _fake_compute(o: OHLCV) -> Indicators | None:
    return _BY_ID.get(id(o))


async def _screen(limit: int | None = None):
    return await screen_service.build_screen(
        cfg=StrategyConfig(), symbols=_UNIVERSE, quote=_quote, limit=limit
    )


async def _run() -> None:
    screen_service.compute = _fake_compute  # inject fixture indicators

    a, b = await _screen(), await _screen()
    check("ScreenResult byte-identical across two runs", a.model_dump_json() == b.model_dump_json())
    check("universe_size counts every resolved symbol", a.universe_size == len(_UNIVERSE),
          str(a.universe_size))

    syms = [c.symbol for c in a.candidates]
    check("only gate-passing symbols ranked (ALFA, BETA)", syms == ["ALFA", "BETA"], str(syms))
    check("GAMMA gated out (low ADX / overbought)", "GAMMA" not in syms)
    check("DELTA skipped (no price data)", "DELTA" not in syms)
    check("ranked by score (ALFA > BETA)", a.candidates[0].score >= a.candidates[1].score)
    check("entry < target and stop < entry", all(
        c.stop_price < c.entry_price < c.target_price for c in a.candidates))

    capped = await _screen(limit=1)
    check("top_n / limit caps the list", len(capped.candidates) == 1, str(len(capped.candidates)))

    print(f"\n── ScreenResult (config {a.config_hash}, universe {a.universe_mode}, "
          f"{a.universe_size} symbols)")
    for c in a.candidates:
        print(f"  {c.symbol:6} score {c.score:.3f}  entry {c.entry_price} stop {c.stop_price} "
              f"target {c.target_price}  {c.reason}")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ signals screen FAILED" if _fail else "✅ signals screen is deterministic"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
