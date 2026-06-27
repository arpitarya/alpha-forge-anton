"""Cross-sectional factor config — the knobs edge-001 ranks, filters, and trades on.

`FactorConfig` is one point in the declared 24-config trial grid (`grid_24()`); `headline()`
is the pre-registered headline (lookback 12 / decile / θ_roce 15 / θ_de 0.5 / trend+stop on).
The grid is the multiple-testing universe PBO / Deflated-Sharpe are scoped to — pinned here,
committed into elgar://edge/edge-001. Pure config, no clock.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

Slice = Literal["decile", "quartile"]
_DAYS_PER_MONTH = 21  # trading days; ret_12_1 = price[t-21]/price[t-252]-1


class FactorConfig(BaseModel):
    lookback_months: int = 12
    skip_month: bool = True  # skip the most recent ~21d (the "_1" gap in 12_1 momentum)
    slice: Slice = "decile"
    theta_roce: float = 15.0  # keep ROCE ≥ this (%)
    theta_de: float = 0.5  # keep debt/equity ≤ this
    trend_on: bool = True  # flat to cash when NIFTY < 200-DMA
    stop_on: bool = True  # 20-day-low stop in addition to the -20% guard

    @property
    def lookback_days(self) -> int:
        return self.lookback_months * _DAYS_PER_MONTH

    @property
    def skip_days(self) -> int:
        return _DAYS_PER_MONTH if self.skip_month else 0


def headline() -> FactorConfig:
    """The pre-registered headline config — the one Gate-1's point backtest runs."""
    return FactorConfig()


def grid_24() -> list[FactorConfig]:
    """The locked 24-config trial grid (PBO/DSR scope). Block A (18) + Block B (6)."""
    cfgs: list[FactorConfig] = []
    for lb in (9, 12, 15):  # Block A: factorial at θ_de=0.5, both slices
        for sl in ("decile", "quartile"):
            for roce in (12.0, 15.0, 18.0):
                cfgs.append(
                    FactorConfig(lookback_months=lb, slice=sl, theta_roce=roce, theta_de=0.5)
                )
    for lb in (9, 12, 15):  # Block B: θ_de=1.0 sensitivity, decile only, θ_roce {12,15}
        for roce in (12.0, 15.0):
            cfgs.append(
                FactorConfig(lookback_months=lb, slice="decile", theta_roce=roce, theta_de=1.0)
            )
    return cfgs
