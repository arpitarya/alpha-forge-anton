"""Shape the funnel's scored gates into the Phase-0 TestReport (+ run metadata).

Split out of `funnel.py` so the orchestrator stays ≤100 lines once the provenance / quality-leg /
universe-status fields are populated. Pure — no compute, just mapping already-scored gate results
into the contract. `RunMeta` carries what the panel/run knows (where the data came from, the date
range, whether the quality leg ran, how the universe was formed) so a real run is self-describing.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.contracts.testreport_contract import QualityStatus, TestReport, Walkforward
from app.modules.edges.edge_schema import EdgeSpec, GateResult
from app.modules.edges.edge_stats import ResultStats


@dataclass(frozen=True)
class RunMeta:
    data_provenance: str
    date_from: str
    date_to: str
    quality_status: QualityStatus
    quality_pending: int
    universe_status: str
    exclusions_count: int = 0
    exclusions_source: str = "none"


def build_report(
    spec: EdgeSpec,
    hs: ResultStats,
    p: float,
    dsr: float,
    hc_t: float,
    g1: bool,
    g2: GateResult,
    survives: bool,
    meta: RunMeta,
) -> TestReport:
    wins = sum(1 for w in g2.windows if w.expectancy_pct > 0)
    return TestReport(
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
        data_provenance=meta.data_provenance,
        date_from=meta.date_from,
        date_to=meta.date_to,
        quality_status=meta.quality_status,
        quality_pending=meta.quality_pending,
        universe_status=meta.universe_status,
        exclusions_count=meta.exclusions_count,
        exclusions_source=meta.exclusions_source,
    )
