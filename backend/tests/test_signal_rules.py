"""Per-branch unit tests for the deterministic swing ruleset.

Pure (no I/O, no network): each test crafts `Indicators` + `HoldingFacts` so that
exactly one verdict branch fires, and asserts the action + that thresholds came
from `StrategyConfig` (changing a knob changes the verdict).

    uv run pytest tests/test_signal_rules.py -v
"""

from __future__ import annotations

from app.modules.signals.indicators import Indicators
from app.modules.signals.signal_rules import HoldingFacts, evaluate
from app.modules.signals.signal_schema import Action
from app.modules.signals.strategy_config import StrategyConfig

CFG = StrategyConfig()  # built-in defaults == the git-safe seed


def _ind(
    close=100.0,
    rsi=58.0,
    adx=30.0,
    dma50=90.0,
    dma200=80.0,
    atr=2.0,
    recent_high=104.0,
    pos=0.8,
    vol=1.1,
) -> Indicators:
    return Indicators(
        close=close,
        rsi14=rsi,
        adx14=adx,
        dma50=dma50,
        dma200=dma200,
        atr14=atr,
        recent_high=recent_high,
        pos_52w=pos,
        vol_ratio=vol,
    )


def _facts(**kw) -> HoldingFacts:
    base = {"symbol": "TEST", "avg_price": 90.0, "pnl_pct": 5.0, "weight_pct": 5.0, "covered": True}
    return HoldingFacts(**{**base, **kw})


def test_sell_hard_stop():
    v = evaluate(_facts(pnl_pct=-20.0), _ind(), CFG)
    assert v.action is Action.SELL and "hard stop" in v.reason and v.stop_price is not None


def test_sell_trailing_atr():
    # close far below recent_high - 2.5*ATR => trailing stop breached
    v = evaluate(_facts(pnl_pct=0.0), _ind(close=100.0, recent_high=130.0, atr=5.0), CFG)
    assert v.action is Action.SELL and "trailing ATR" in v.reason


def test_sell_below_dma_weak_rsi():
    v = evaluate(_facts(pnl_pct=0.0), _ind(close=80.0, dma50=90.0, rsi=35.0, recent_high=82.0), CFG)
    assert v.action is Action.SELL and "DMA50" in v.reason


def test_trim_profit():
    v = evaluate(_facts(pnl_pct=60.0), _ind(), CFG)
    assert v.action is Action.TRIM and v.target_price is not None


def test_trim_concentration():
    v = evaluate(_facts(pnl_pct=10.0, weight_pct=20.0), _ind(), CFG)
    assert v.action is Action.TRIM and "cap" in v.reason


def test_add_continuation_needs_catalyst():
    strong = _ind(close=100.0, dma50=90.0, adx=30.0, rsi=60.0, pos=0.95, recent_high=101.0)
    assert evaluate(_facts(pnl_pct=10.0, catalyst=True), strong, CFG).action is Action.ADD
    # same setup without a catalyst must NOT add (conservative) -> HOLD
    assert evaluate(_facts(pnl_pct=10.0, catalyst=False), strong, CFG).action is Action.HOLD


def test_hold_nearest_trigger():
    v = evaluate(_facts(pnl_pct=20.0), _ind(), CFG)
    assert v.action is Action.HOLD and "below trim level" in v.reason


def test_not_covered_and_no_data():
    assert evaluate(_facts(covered=False), _ind(), CFG).action is Action.HOLD
    assert evaluate(_facts(), None, CFG).action is Action.HOLD


def test_thresholds_come_from_config():
    # raising the hard-stop knob flips a -16% holding from SELL to not-SELL
    loose = StrategyConfig.model_validate({"stops": {"hard_pct": -25}})
    assert evaluate(_facts(pnl_pct=-16.0), _ind(), CFG).action is Action.SELL
    assert evaluate(_facts(pnl_pct=-16.0), _ind(), loose).action is not Action.SELL
