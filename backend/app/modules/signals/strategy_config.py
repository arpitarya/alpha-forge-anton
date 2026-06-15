"""Load + validate the tunable strategy knobs into a typed `StrategyConfig`.

Single source of truth for every decision threshold (handoff §6.5) — `signal_rules`,
`screener_rules`, `universe`, and the Parallel budget all read from here, never
hardcode. Resolution: elgar `strategy/` (live, Orff-editable) → git-safe repo seed
`strategy.config.md` → defaults. Sync load (like `plan_loader` / `env_loader`).
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field


class UniverseCfg(BaseModel):
    mode: Literal["themes", "nifty500"] = "themes"
    themes: list[str] = Field(
        default_factory=lambda: ["defence", "solar", "capex_td", "ev_auto", "specialty_chem"]
    )


class TrimRule(BaseModel):
    mode: Literal["trail", "trim_half"] = "trail"
    trim_at_pct: float = 50.0
    trail_atr_mult: float = 2.5
    max_weight_pct: float = 15.0  # concentration cap, % of equity book


class Stops(BaseModel):
    hard_pct: float = -15.0


class ExitRule(BaseModel):
    weak_rsi: float = 40.0  # RSI below which a sub-DMA50 close becomes a SELL


class Entry(BaseModel):
    min_adx: float = 25.0
    rsi_band: tuple[float, float] = (50.0, 70.0)
    high_52w_min: float = 0.90


class ScreenerCfg(BaseModel):
    min_vol_ratio: float = 1.5  # volume breakout gate (last vol / 20-day avg)
    top_n: int = 10  # number of ranked candidates returned


class CostsCfg(BaseModel):
    # Friction + tax for the net-P&L tracker (§10.4). Rates change in Finance Acts —
    # verify before trusting a number (see Fux transaction-costs / capital-gains-equity).
    brokerage_per_order_inr: float = 20.0  # flat per executed order (Zerodha delivery = 0)
    stt_pct: float = 0.1  # delivery STT, % of value per leg
    friction_pct: float = 0.03  # stamp + exchange + SEBI + GST, % of turnover
    stcg_pct: float = 20.0  # §111A short-term capital gains, %


class ParallelCfg(BaseModel):
    monthly_budget_inr: float = 300.0
    allow_task_api: bool = True


class StrategyConfig(BaseModel):
    universe: UniverseCfg = Field(default_factory=UniverseCfg)
    trim_rule: TrimRule = Field(default_factory=TrimRule)
    stops: Stops = Field(default_factory=Stops)
    exit: ExitRule = Field(default_factory=ExitRule)
    entry: Entry = Field(default_factory=Entry)
    screener: ScreenerCfg = Field(default_factory=ScreenerCfg)
    costs: CostsCfg = Field(default_factory=CostsCfg)
    parallel: ParallelCfg = Field(default_factory=ParallelCfg)

    def hash(self) -> str:
        """Stable 12-char digest — the determinism anchor stamped onto an ActionPlan."""
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()[:12]


# Loading lives in config_loader (line budget); re-exported here so strategy_config
# stays the import surface for `load_config` / `_config_paths`. After StrategyConfig.
from app.modules.signals.config_loader import _config_paths, load_config  # noqa: E402, F401
