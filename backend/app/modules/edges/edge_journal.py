"""The discovery journal — every run, pass OR kill, is recorded with its stats.

A kept hypothesis and a killed one are equally informative: the journal is the audit
trail that stops survivorship bias (you only remember the winners). One record per
`discover` run carries the edge id, the highest gate reached, pass/kill, and the gate
results. It lives in the elgar `edges-journal` collection (best-effort, like the spec
store) — stats and counts only, no holdings or ₹ PII, so it's safe by construction.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.modules.edges.edge_schema import GateResult
from app.modules.plans import elgar_bridge

logger = logging.getLogger(__name__)

_COLLECTION = "edges-journal"


class JournalRecord(BaseModel):
    """One discovery run's outcome — the unit the journal appends."""

    edge_id: str
    run_at: str  # ISO UTC — when the backtest ran (lives here, not in a GateResult)
    gate_reached: int = 0
    passed: bool = False
    gates: list[GateResult] = Field(default_factory=list)


def build_record(edge_id: str, run_at: datetime, gates: list[GateResult]) -> JournalRecord:
    reached = max((g.gate for g in gates if g.passed), default=0)
    passed = bool(gates) and all(g.passed for g in gates)
    return JournalRecord(
        edge_id=edge_id,
        run_at=run_at.astimezone(UTC).isoformat(),
        gate_reached=reached,
        passed=passed,
        gates=gates,
    )


def _doc(rec: JournalRecord) -> str:
    verdict = "PASS" if rec.passed else "KILL"
    return (
        f"---\nedge: {rec.edge_id}\nrun_at: {rec.run_at}\nverdict: {verdict}\n"
        f"gate_reached: {rec.gate_reached}\n---\n# {verdict} — {rec.edge_id}\n\n"
        f"```json\n{rec.model_dump_json(indent=2)}\n```\n"
    )


async def append(rec: JournalRecord) -> str | None:
    entry_id = f"{rec.edge_id}-{rec.run_at.replace(':', '').replace('-', '')[:15]}"
    try:
        return await elgar_bridge.save(
            entry_id, _doc(rec), message=f"orff: journal {entry_id}", collection=_COLLECTION
        )
    except Exception as e:  # best-effort — journaling never blocks discovery
        logger.warning("journal append failed: %s", e)
        return None
