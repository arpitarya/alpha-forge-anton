"""Run the funnel for one cockpit edge — invoke it whole, never rewrite a gate.

The debut runs **edge-001** against the REAL nse-bhavcopy panel with the exact
`eb0_real` parameters (seed 0, quality disabled-pending, no point-in-time feed), so a
UI-triggered run is **byte-identical** to the CLI run (the determinism contract). The
heavy 24-config + Monte-Carlo compute runs in a worker thread (`asyncio.to_thread`) so it
never blocks the event loop. The ₹-free `TestReport` is journaled to elgar, never here.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.modules.edges import edge_journal, edge_store
from app.modules.edges.eb0_cli import edge_001
from app.modules.edges.eb0_real_cli import _NO_FEED, _REAL
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.edges.factor_panel import load_panel
from app.modules.edges.funnel import FunnelResult, run_funnel
from app.modules.flow.flow_run_schema import GateProgress, GateState

# The locked funnel gates the cockpit renders. 0 = the panel-build integrity gate (Gate-0).
GATES: list[tuple[int, str]] = [
    (0, "Integrity"),
    (1, "Backtest + overfitting"),
    (2, "Walk-forward"),
    (3, "Outcome cone"),
]


async def resolve_spec(edge_id: str) -> EdgeSpec | None:
    """The runnable spec for an edge — edge-001's pinned campaign, else the UI-authored spec."""
    if edge_id == "edge-001":
        return edge_001()  # the pinned spec the CLI runs — keeps the UI run byte-identical
    return await edge_store.load(edge_id)


def _compute(spec: EdgeSpec) -> FunnelResult:
    """CPU-bound funnel run — executed in a worker thread (its own loop), off the event loop."""
    return asyncio.run(
        run_funnel(
            spec,
            load_panel(_REAL),
            _NO_FEED,
            seed=0,
            data_provenance="nse-bhavcopy",
            quality_on=False,
        )
    )


async def run_edge(edge_id: str) -> FunnelResult:
    """Resolve, run off-loop, and journal one edge's verdict. Fail-loud on no panel/spec."""
    spec = await resolve_spec(edge_id)
    if spec is None:
        raise FileNotFoundError(
            f"no runnable spec for {edge_id!r} — author + pre-register it first"
        )
    if not _REAL.exists():
        raise FileNotFoundError(
            "no real NSE panel — run `just ingest-nse FROM TO` then `just build-panel`"
        )
    result = await asyncio.to_thread(_compute, spec)
    await edge_journal.append(edge_journal.from_report(result.report, datetime.now(UTC)))
    return result


def gates_from_report(report) -> list[GateProgress]:
    """Per-gate progress from a completed report — passed/failed(killer)/skipped, deterministic."""
    passed = set(report.gates_passed)
    out = [GateProgress(gate=0, label="Integrity", state=GateState.PASSED)]  # panel is Gate-0 clean
    killed = False
    for gate, label in GATES[1:]:
        if gate in passed:
            out.append(GateProgress(gate=gate, label=label, state=GateState.PASSED))
        elif not killed:
            out.append(GateProgress(gate=gate, label=label, state=GateState.FAILED))
            killed = True
        else:
            out.append(GateProgress(gate=gate, label=label, state=GateState.SKIPPED))
    return out
