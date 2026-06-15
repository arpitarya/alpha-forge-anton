"""Pure buy-candidate screener — the entry mirror of the ADD rule (handoff §6).

A universe symbol becomes a `Candidate` only if it clears every entry gate, then
gets a deterministic rank score. Gates/cutoffs come from `StrategyConfig`
(`entry.*` + `screener.*`); the scoring *weights* are fixed code constants (a
formula, not a tunable decision boundary). No I/O, no clock.
"""

from __future__ import annotations

from app.modules.signals.indicators import Indicators
from app.modules.signals.signal_schema import Candidate
from app.modules.signals.strategy_config import StrategyConfig

_W_ADX, _W_POS, _W_VOL = 0.40, 0.35, 0.25  # rank-score weights (sum to 1)


def _norm_adx(adx: float) -> float:
    return min(adx / 50.0, 1.0)


def _norm_vol(vol_ratio: float) -> float:
    return min(vol_ratio / 3.0, 1.0)


def screen_one(symbol: str, ind: Indicators, cfg: StrategyConfig) -> Candidate | None:
    lo, hi = cfg.entry.rsi_band
    passes = (
        ind.adx14 > cfg.entry.min_adx
        and ind.pos_52w >= cfg.entry.high_52w_min
        and ind.close > ind.dma50
        and lo <= ind.rsi14 <= hi
        and ind.vol_ratio >= cfg.screener.min_vol_ratio
    )
    if not passes:
        return None
    close = ind.close
    stop = round(close - cfg.trim_rule.trail_atr_mult * ind.atr14, 2)
    target = round(close + 2 * (close - stop), 2)
    score = round(
        _W_ADX * _norm_adx(ind.adx14) + _W_POS * ind.pos_52w + _W_VOL * _norm_vol(ind.vol_ratio), 4
    )
    reason = f"ADX {ind.adx14:.0f}, {ind.pos_52w * 100:.0f}% of 52w range, vol {ind.vol_ratio:.1f}x"
    return Candidate(
        symbol=symbol,
        score=score,
        entry_price=round(close, 2),
        stop_price=stop,
        target_price=target,
        adx=round(ind.adx14, 2),
        rsi=round(ind.rsi14, 2),
        pos_52w=ind.pos_52w,
        reason=reason,
    )


def rank(candidates: list[Candidate], top_n: int) -> list[Candidate]:
    """Highest score first; ties broken by symbol for a deterministic order."""
    return sorted(candidates, key=lambda c: (-c.score, c.symbol))[:top_n]
