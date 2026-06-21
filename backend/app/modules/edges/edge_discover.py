"""The discovery loop — pre-registration check → gate 1 → gate 2 → journal.

Orchestrates the engine for one pre-registered edge. The pre-registration assertion
runs FIRST: no result is computed or recorded for a hypothesis dated after the run.
Gate 2 only runs if gate 1 passes (a no-edge candidate is killed cheaply). Every run,
pass or kill, is journaled. `run_at` is injected so the loop is deterministic/testable;
default is now(UTC). Returns the gate results so the CLI/probe can render them.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.modules.edges import edge_journal
from app.modules.edges.edge_backtest import run_gate1
from app.modules.edges.edge_data import BarsProvider, NSEDailyBars
from app.modules.edges.edge_register import assert_pre_registered
from app.modules.edges.edge_schema import EdgeSpec, GateResult
from app.modules.edges.edge_walkforward import run_gate2
from app.modules.signals.strategy_config import CostsCfg


async def discover(
    spec: EdgeSpec,
    provider: BarsProvider | None = None,
    costs: CostsCfg | None = None,
    run_at: datetime | None = None,
    journal: bool = True,
) -> list[GateResult]:
    run_at = run_at or datetime.now(UTC)
    assert_pre_registered(spec, run_at)  # refuses a post-result hypothesis — before any compute
    provider = provider or NSEDailyBars()
    costs = costs or CostsCfg()

    gates: list[GateResult] = [await run_gate1(spec, provider, costs)]
    if gates[0].passed:
        gates.append(await run_gate2(spec, provider, costs))

    if journal:
        await edge_journal.append(edge_journal.build_record(spec.id, run_at, gates))
    return gates
