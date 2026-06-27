"""EB-0 — push the pre-registered edge-001 through the funnel and print a signed TestReport.

The project's #1 proof, run deterministically offline on the committed panel fixture. edge-001's
pre_registered_at (2026-06-23, elgar commit 753eaee) predates this run, so the result is honest by
construction; the funnel refuses any post-hoc spec. A PASS and an honest KILL are both valid — this
CLI never tunes anything. `just eb0` runs it; a real cached NSE snapshot can replace the fixture.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from app.modules.edges.edge_schema import EdgeSpec
from app.modules.edges.factor_panel import load_panel
from app.modules.edges.factor_quality import FixtureFundamentals
from app.modules.edges.factor_schema import headline
from app.modules.edges.funnel import FunnelResult, run_funnel

_FIX = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "eb0"
EDGE_001_PRE = datetime(2026, 6, 23, tzinfo=UTC)  # frozen pre-registration (elgar 753eaee)


def edge_001() -> EdgeSpec:
    return EdgeSpec(
        id="edge-001",
        hypothesis="cross-sectional 12-1 momentum + quality + NIFTY-trend",
        universe=[],
        signal="momentum",
        holding_period_days=5,
        pre_registered_at=EDGE_001_PRE,
        factor=headline(),
    )


def fundamentals() -> FixtureFundamentals:
    d = json.loads((_FIX / "fundamentals.json").read_text(encoding="utf-8"))
    return FixtureFundamentals(d["roce"], d["debt_equity"])


def render(res: FunnelResult) -> str:
    r = res.report
    out = [
        f"\n== EB-0: {r.edge_id} ==",
        f"verdict: {r.verdict.upper()}   gates_passed={r.gates_passed}",
        f"PBO {r.pbo}  DeflatedSharpe {r.deflated_sharpe}  haircut_t {r.haircut_t}",
        f"WF: calmar {r.walkforward.agg_calmar} pctWin+ {r.walkforward.pct_windows_positive}",
        f"cone es_p5 {res.cone.es_p5}  confidence {res.cone.confidence}",
        f"pre_registered_at {r.pre_registered_at.isoformat() if r.pre_registered_at else None}",
        f"signature {res.signature}",
    ]
    out += [f"  note: {n}" for n in res.notes]
    return "\n".join(out)


async def _amain() -> int:
    res = await run_funnel(edge_001(), load_panel(_FIX / "panel.json"), fundamentals(), seed=0)
    print(render(res))
    print("\nPASS and honest KILL are both valid EB-0 outcomes — nothing here is tuned.")
    return 0


def main() -> int:
    return asyncio.run(_amain())


if __name__ == "__main__":
    raise SystemExit(main())
