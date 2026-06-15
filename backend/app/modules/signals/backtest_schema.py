"""Shapes for the Phase 5 backtest — replay the active config over history (§10.5).

`BacktestConfig` holds the *backtest mechanics* (lookback, cadence, per-trade
notional) — deliberately separate from `StrategyConfig`, which is the thing
under test. `BacktestReport` is the after-cost verdict: positive expectancy or
not. No personal figures — notional is a nominal scale knob, git-safe.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BacktestConfig(BaseModel):
    years: int = 3  # lookback window of daily history to replay
    step_days: int = 5  # walk-forward cadence (5 = weekly, matches the Phase 4 review)
    notional_inr: float = 100_000.0  # fixed equal notional per round-trip (scale only)


class BacktestReport(BaseModel):
    """After-cost replay result — the 'is the edge real' check before sizing up."""

    config_hash: str = ""  # the StrategyConfig the replay ran under
    period: str = ""  # "YYYY-MM-DD..YYYY-MM-DD" covered by the replay
    universe_size: int = 0
    trades: int = 0
    wins: int = 0
    win_rate: float = 0.0  # fraction of round-trips net-positive after frictions
    gross: float = 0.0  # Σ gross P&L before any cost
    net: float = 0.0  # P&L AFTER all costs (brokerage+STT+friction+STCG) — the headline
    expectancy_inr: float = 0.0  # mean per-trade net after frictions (the trading edge)
    expectancy_pct: float = 0.0  # expectancy as % of notional
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0  # Σwins / |Σlosses|; >1 means the edge survives losers
    max_drawdown: float = 0.0  # deepest peak-to-trough on the cumulative net curve, ₹
    max_drawdown_pct: float = 0.0  # as % of the peak equity
    positive_expectancy: bool = False  # net>0 AND expectancy>0 — the go/no-go flag
    notes: list[str] = Field(default_factory=list)
