"""Unit tests for the buy-candidate screener — gates + deterministic ranking.

Pure (no I/O): craft `Indicators` so each entry gate can be isolated, and assert
the ranking is score-ordered and config-driven.

    uv run pytest tests/test_screener_rules.py -v
"""

from __future__ import annotations

from app.modules.signals.indicators import Indicators
from app.modules.signals.screener_rules import rank, screen_one
from app.modules.signals.strategy_config import StrategyConfig

CFG = StrategyConfig()  # defaults: min_adx 25, rsi [50,70], 52w≥0.90, min_vol_ratio 1.5


def _ind(adx=30.0, pos=0.95, close=100.0, dma50=90.0, rsi=60.0, vol=2.0, atr=2.0) -> Indicators:
    return Indicators(
        close=close,
        rsi14=rsi,
        adx14=adx,
        dma50=dma50,
        dma200=80.0,
        atr14=atr,
        recent_high=close,
        pos_52w=pos,
        vol_ratio=vol,
    )


def test_passes_all_gates_builds_candidate():
    c = screen_one("HAL", _ind(), CFG)
    assert c is not None
    assert c.entry_price == 100.0 and c.stop_price < c.entry_price < c.target_price
    assert 0 < c.score <= 1


def test_each_gate_can_reject():
    assert screen_one("X", _ind(adx=20.0), CFG) is None  # ADX below min
    assert screen_one("X", _ind(pos=0.5), CFG) is None  # not near 52w high
    assert screen_one("X", _ind(close=80.0, dma50=90.0), CFG) is None  # below DMA50
    assert screen_one("X", _ind(rsi=80.0), CFG) is None  # RSI outside band
    assert screen_one("X", _ind(vol=1.0), CFG) is None  # no volume breakout


def test_rank_is_score_sorted_then_symbol_and_capped():
    weak = screen_one("ZEE", _ind(adx=26.0, pos=0.90, vol=1.6), CFG)
    strong = screen_one("AAA", _ind(adx=45.0, pos=0.99, vol=3.0), CFG)
    out = rank([weak, strong], top_n=1)
    assert [c.symbol for c in out] == ["AAA"]  # higher score first, top_n respected


def test_thresholds_come_from_config():
    weak_vol = _ind(vol=1.2)  # fails default min_vol_ratio 1.5
    assert screen_one("X", weak_vol, CFG) is None
    loose = StrategyConfig.model_validate({"screener": {"min_vol_ratio": 1.0}})
    assert screen_one("X", weak_vol, loose) is not None
