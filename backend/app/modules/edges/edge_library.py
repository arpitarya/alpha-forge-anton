"""Read side of the discovery journal — the edge-library stats the Goals tab shows.

Reads the structured `journal.jsonl` mirror (`edge_journal` emits one line per run),
and tolerates legacy markdown-only entries by parsing the ```json block each embeds —
so a journal written before the mirror existed still counts, never crashes. Records are
deduped by (edge_id, run_at), then grouped by edge: one edge tested many times counts
once. `live` is 0 until a promotion source exists; `kill_rate = killed / tested`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel

from app.modules.edges.edge_journal import JournalRecord, jsonl_path

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


class RecentRun(BaseModel):
    edge_id: str
    run_at: str
    verdict: str  # PASS | KILL
    gate_reached: int = 0


class EdgeLibrarySummary(BaseModel):
    """Edge-library funnel — counts only, constitutionally safe (no ₹, no holdings)."""

    tested: int = 0
    killed: int = 0
    passed: int = 0
    live: int = 0  # promoted to real capital — none yet
    kill_rate: float = 0.0  # killed / tested (0.0-1.0)
    recent: list[RecentRun] = []


def _from_jsonl(path: Path) -> list[JournalRecord]:
    if not path.exists():
        return []
    out: list[JournalRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(JournalRecord.model_validate_json(line))
    return out


def _from_markdown(journal_dir: Path) -> list[JournalRecord]:
    out: list[JournalRecord] = []
    for md in journal_dir.glob("*.md"):
        match = _JSON_BLOCK.search(md.read_text(encoding="utf-8"))
        if match:
            out.append(JournalRecord.model_validate(json.loads(match.group(1))))
    return out


def _records() -> list[JournalRecord]:
    """All journal records, deduped by (edge_id, run_at) across jsonl + legacy md."""
    path = jsonl_path()
    seen = _from_jsonl(path) + _from_markdown(path.parent)
    return list({(r.edge_id, r.run_at): r for r in seen}.values())


def library_summary() -> EdgeLibrarySummary:
    """Aggregate the journal into the edge-library funnel. Empty journal → all zeros."""
    by_edge: dict[str, JournalRecord] = {}
    for rec in sorted(_records(), key=lambda r: r.run_at):
        by_edge[rec.edge_id] = rec  # latest run per edge wins
    tested = len(by_edge)
    passed = sum(1 for r in by_edge.values() if r.passed)
    killed = tested - passed
    recent = sorted(
        (RecentRun(edge_id=r.edge_id, run_at=r.run_at,
                   verdict="PASS" if r.passed else "KILL", gate_reached=r.gate_reached)
         for r in by_edge.values()),
        key=lambda r: r.run_at, reverse=True,
    )[:5]
    return EdgeLibrarySummary(
        tested=tested, killed=killed, passed=passed, live=0,
        kill_rate=round(killed / tested, 4) if tested else 0.0, recent=recent,
    )
