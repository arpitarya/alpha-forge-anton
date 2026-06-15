"""The deterministic swing ruleset — `(facts, indicators, config) -> Verdict`.

Pure: no I/O, no clock, no LLM. Every threshold is read from `StrategyConfig`
(handoff §6/§6.5) so the strategy is tunable through Orff without code changes.
Rules evaluate in priority order — SELL > TRIM > ADD > HOLD, first match wins.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.signals.indicators import Indicators
from app.modules.signals.signal_schema import Action, Verdict
from app.modules.signals.strategy_config import StrategyConfig


@dataclass
class HoldingFacts:
    symbol: str
    avg_price: float
    pnl_pct: float
    weight_pct: float  # share of the equity book
    covered: bool  # INR-listed equity with data — the swing universe
    catalyst: bool = False  # a matched news catalyst (wired in Phase 3)


def _v(symbol, action, reason, *, stop=None, target=None, conv=0) -> Verdict:
    return Verdict(
        symbol=symbol,
        action=action,
        reason=reason,
        stop_price=stop,
        target_price=target,
        conviction=conv,
    )


def _levels(
    close: float, avg: float, ind: Indicators, cfg: StrategyConfig
) -> tuple[float, float | None]:
    """stop = max(hard-stop price, trailing-ATR stop); target = 2R above stop."""
    hard = avg * (1 + cfg.stops.hard_pct / 100)
    trail = ind.recent_high - cfg.trim_rule.trail_atr_mult * ind.atr14
    stop = round(max(hard, trail), 2)
    target = round(close + 2 * (close - stop), 2) if stop < close else None
    return stop, target


def evaluate(f: HoldingFacts, ind: Indicators | None, cfg: StrategyConfig) -> Verdict:
    if not f.covered:
        return _v(f.symbol, Action.HOLD, "not covered by the swing ruleset (US/non-equity)")
    if ind is None:
        return _v(f.symbol, Action.HOLD, "no price data")

    close = ind.close
    stop, target = _levels(close, f.avg_price, ind, cfg)
    trail = ind.recent_high - cfg.trim_rule.trail_atr_mult * ind.atr14

    triggers: list[str] = []
    if f.pnl_pct < cfg.stops.hard_pct:
        triggers.append(f"hard stop {cfg.stops.hard_pct:.0f}%")
    if close < trail:
        triggers.append("trailing ATR stop hit")
    if close < ind.dma50 and ind.rsi14 < cfg.exit.weak_rsi:
        triggers.append(f"below DMA50 & RSI<{cfg.exit.weak_rsi:.0f}")
    if triggers:
        return _v(
            f.symbol, Action.SELL, "; ".join(triggers), stop=stop, conv=min(len(triggers) + 1, 5)
        )

    if f.pnl_pct > cfg.trim_rule.trim_at_pct:
        tail = "book half" if cfg.trim_rule.mode == "trim_half" else "tighten the trailing stop"
        reason = f"+{f.pnl_pct:.0f}% ≥ trim level — {tail}"
        return _v(f.symbol, Action.TRIM, reason, stop=stop, target=target, conv=2)
    if f.weight_pct > cfg.trim_rule.max_weight_pct:
        reason = f"{f.weight_pct:.0f}% of book > {cfg.trim_rule.max_weight_pct:.0f}% cap"
        return _v(f.symbol, Action.TRIM, reason, stop=stop, target=target, conv=2)

    lo, hi = cfg.entry.rsi_band
    if (
        ind.pos_52w >= cfg.entry.high_52w_min
        and ind.adx14 > cfg.entry.min_adx
        and close > ind.dma50
        and lo <= ind.rsi14 <= hi
        and f.catalyst
    ):
        reason = "near 52w high, strong ADX, RSI in band + catalyst"
        return _v(f.symbol, Action.ADD, reason, stop=stop, target=target, conv=3)

    gap = cfg.trim_rule.trim_at_pct - f.pnl_pct
    return _v(
        f.symbol, Action.HOLD, f"{gap:.0f}% below trim level", stop=stop, target=target, conv=1
    )
