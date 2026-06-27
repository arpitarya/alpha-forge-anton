"""Weekly cross-sectional simulator → the net-return series the funnel scores.

Each weekly rebalance it re-forms the sleeve (rank → top slice → quality → trend), holds it for
the week, and books each name as an independent round-trip netted through `edge_costs.net_pct`
(STCG + frictions + slippage). The week's portfolio return is the equal-weight mean of those
net legs (0% in cash weeks). **v1 cost model is deliberately conservative**: it pays a full
round-trip cost every week rather than amortising persistence, so it *over*-charges turnover —
the safe direction for a discovery funnel (an edge must clear even a strict cost bar). Pure and
deterministic: same panel + config ⇒ same series; pending quality names are counted, not faked.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.modules.edges.edge_costs import net_pct
from app.modules.edges.factor_exits import leg_exit
from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_quality import FundamentalsProvider, quality_filter
from app.modules.edges.factor_rank import rank_desc, select
from app.modules.edges.factor_schema import FactorConfig
from app.modules.edges.factor_trend import nifty_above_200dma
from app.modules.signals.strategy_config import CostsCfg

_WEEK = 5  # trading days between rebalances (and the per-leg holding window)


@dataclass(frozen=True)
class SleeveResult:
    weekly: list[float] = field(
        default_factory=list
    )  # weekly portfolio net %; feeds build_stats + MC
    trades: list[float] = field(default_factory=list)  # per-name net round-trip %
    pending: int = 0  # honest-pending quality screens skipped (count only)


def _sleeve(panel: Panel, t: int, cfg: FactorConfig, fund: FundamentalsProvider, quality_on: bool):
    if cfg.trend_on and not nifty_above_200dma(panel.nifty, t):
        return [], []  # cash week
    picked = select(rank_desc(panel, t, cfg), cfg.slice)
    if not quality_on:  # no point-in-time feed → momentum+trend only; names counted as pending
        return picked, picked
    return quality_filter(picked, cfg, fund)


def _start(cfg: FactorConfig) -> int:
    # need momentum history, plus a 200-DMA reading only when the trend filter is on
    return max(cfg.lookback_days, 200) if cfg.trend_on else cfg.lookback_days


def simulate(
    panel: Panel,
    cfg: FactorConfig,
    fund: FundamentalsProvider,
    costs: CostsCfg | None = None,
    quality_on: bool = True,
) -> SleeveResult:
    costs = costs or CostsCfg()
    last = len(panel.dates) - 1
    weekly: list[float] = []
    trades: list[float] = []
    pending = 0
    t = _start(cfg)
    while t + _WEEK <= last:
        kept, pend = _sleeve(panel, t, cfg, fund, quality_on)
        pending += len(pend)
        legs: list[float] = []
        for sym in kept:
            closes = panel.closes[sym]
            ex_t, _ = leg_exit(closes, t, _WEEK, cfg)
            net = net_pct(
                closes[t],
                closes[ex_t],
                1.0,
                date.fromisoformat(panel.dates[t]),
                date.fromisoformat(panel.dates[ex_t]),
                costs,
            )
            legs.append(net)
        trades += legs
        weekly.append(sum(legs) / len(legs) if legs else 0.0)
        t += _WEEK
    return SleeveResult(weekly=weekly, trades=trades, pending=pending)
