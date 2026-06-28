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
from pathlib import Path

from pydantic import BaseModel, Field

from app.modules.contracts.testreport_contract import TestReport
from app.modules.edges.edge_schema import GateResult
from app.modules.plans import elgar_bridge
from app.modules.plans.elgar_store import store_root

logger = logging.getLogger(__name__)

_COLLECTION = "edges-journal"


def jsonl_path() -> Path:
    """Append-only structured mirror of the journal — one JSON record per run, so
    the read side (`edge_library`) never parses markdown. Lives in the elgar store
    (root from elgar; Anton owns no path)."""
    return store_root() / _COLLECTION / "journal.jsonl"


class JournalRecord(BaseModel):
    """One discovery run's outcome — the unit the journal appends."""

    edge_id: str
    run_at: str  # ISO UTC — when the backtest ran (lives here, not in a GateResult)
    gate_reached: int = 0
    passed: bool = False
    gates: list[GateResult] = Field(default_factory=list)
    report: dict | None = None  # full TestReport (stats/% — no ₹) when journaling a real result


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


def from_report(report: TestReport, run_at: datetime) -> JournalRecord:
    """Build a journal record from a funnel TestReport — stats only, constitutionally safe."""
    return JournalRecord(
        edge_id=report.edge_id,
        run_at=run_at.astimezone(UTC).isoformat(),
        gate_reached=max(report.gates_passed, default=0),
        passed=report.verdict == "pass",
        report=report.model_dump(mode="json"),
    )


def _doc(rec: JournalRecord) -> str:
    verdict = "PASS" if rec.passed else "KILL"
    return (
        f"---\nedge: {rec.edge_id}\nrun_at: {rec.run_at}\nverdict: {verdict}\n"
        f"gate_reached: {rec.gate_reached}\n---\n# {verdict} — {rec.edge_id}\n\n"
        f"```json\n{rec.model_dump_json(indent=2)}\n```\n"
    )


def _append_jsonl(rec: JournalRecord) -> None:
    """Mirror the record as one JSONL line — best-effort, stats-only (no ₹/PII)."""
    try:
        path = jsonl_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(rec.model_dump_json() + "\n")
    except Exception as e:  # never block discovery on the mirror
        logger.warning("journal jsonl append failed: %s", e)


async def append(rec: JournalRecord) -> str | None:
    _append_jsonl(rec)
    entry_id = f"{rec.edge_id}-{rec.run_at.replace(':', '').replace('-', '')[:15]}"
    try:
        return await elgar_bridge.save(
            entry_id, _doc(rec), message=f"orff: journal {entry_id}", collection=_COLLECTION
        )
    except Exception as e:  # best-effort — journaling never blocks discovery
        logger.warning("journal append failed: %s", e)
        return None
