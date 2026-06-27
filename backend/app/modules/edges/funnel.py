"""The funnel core — push a pre-registered cross-sectional edge through Gates 1-3.

Orchestrates the honest pipeline: pre-registration check FIRST, then Gate 1 (backtest the headline
config + the 24-config overfitting statistics: PBO, Deflated Sharpe, Harvey-Liu haircut, with N
read from the trial-ledger), Gate 2 (walk-forward), Gate 3 (Monte-Carlo cone). Emits a Phase-0
`TestReport` plus a deterministic sha256 signature (same panel + seed => same report => same
signature). A PASS and an honest KILL are both valid outcomes; nothing here tunes to force a pass.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from app.modules.contracts.cone_contract import Cone
from app.modules.contracts.testreport_contract import TestReport, Walkforward
from app.modules.edges import trial_ledger
from app.modules.edges.cscv_pbo import pbo
from app.modules.edges.deflated_sharpe import deflated_sharpe, sharpe
from app.modules.edges.edge_register import assert_pre_registered
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.edges.edge_stats import build_stats
from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_quality import FundamentalsProvider
from app.modules.edges.factor_rebalance import simulate
from app.modules.edges.factor_schema import grid_24, headline
from app.modules.edges.factor_walkforward import walk_forward
from app.modules.edges.gate3_montecarlo import montecarlo_cone
from app.modules.edges.harvey_liu import haircut
from app.modules.signals.strategy_config import CostsCfg

PBO_MAX = 0.5  # selecting the best backtest must beat a coin flip
DSR_MIN = 0.95  # 95% confidence the Sharpe survives N-trial deflation
_HOLD = 5  # weekly cadence (build_stats annualisation unit)


@dataclass(frozen=True)
class FunnelResult:
    report: TestReport
    cone: Cone
    signature: str
    notes: list[str]


async def run_funnel(
    spec: EdgeSpec,
    panel: Panel,
    fund: FundamentalsProvider,
    costs: CostsCfg | None = None,
    seed: int = 0,
    ledger_path=None,
    run_at: datetime | None = None,
    pbo_partitions: int = 16,
    mc_sims: int = 2000,
) -> FunnelResult:
    assert_pre_registered(spec, run_at or datetime.now(UTC))  # refuse post-hoc, before any compute
    costs = costs or CostsCfg()
    grid = grid_24()
    trial_ledger.declare_budget(spec.id, len(grid), ledger_path)
    n_trials = trial_ledger.budget(spec.id, ledger_path)

    series = [simulate(panel, cfg, fund, costs).weekly for cfg in grid]
    head = simulate(panel, headline(), fund, costs).weekly
    hs = build_stats(head, _HOLD)

    p = pbo(series, pbo_partitions)
    dsr = deflated_sharpe(head, [sharpe(s) for s in series], n_trials)
    hc_t, _ = haircut(sharpe(head), len(head), n_trials)
    g1 = hs.trades > 0 and hs.expectancy_pct > 0 and p < PBO_MAX and dsr >= DSR_MIN

    g2 = walk_forward(series)
    cone, survives, red = montecarlo_cone(head, seed=seed, n_sims=mc_sims)

    wins = sum(1 for w in g2.windows if w.expectancy_pct > 0)
    report = TestReport(
        edge_id=spec.id,
        gates_passed=[g for g, ok in ((1, g1), (2, g2.passed), (3, survives)) if ok],
        pbo=p,
        deflated_sharpe=dsr,
        haircut_t=hc_t,
        walkforward=Walkforward(
            agg_calmar=g2.stats.calmar,
            pct_windows_positive=round(wins / len(g2.windows), 4) if g2.windows else 0.0,
        ),
        verdict="pass" if (g1 and g2.passed and survives) else "fail",
        pre_registered_at=spec.pre_registered_at,
    )
    notes = [
        f"gate1 exp {hs.expectancy_pct:+.3f}% PBO {p} DSR {dsr} haircut_t {hc_t} (N={n_trials})",
        f"gate2 {g2.notes[0]}",
        f"gate3 P5 cone {'survives' if survives else 'KILL (breaches -20%)'}; red-team {red}",
    ]
    sig = hashlib.sha256(report.model_dump_json().encode()).hexdigest()
    return FunnelResult(report=report, cone=cone, signature=sig, notes=notes)
