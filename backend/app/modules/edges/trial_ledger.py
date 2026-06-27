"""Append-only trial-budget ledger — the overfitting-penalty integrity the funnel reads.

Multiple-testing is the enemy of edge discovery: try enough hypotheses and one passes by
luck. This ledger records, per edge, the trial budget the author *declared up front* and the
trials actually spent, so Phase 1 can deflate results by how many shots were taken. It is
**append-only** (a correction is a new line, never an edit) and carries **counts only** — no
holdings, no ₹, no prompt text — so it is constitutionally safe by construction, the same
discipline as `edge_journal`. The path is injectable for offline, deterministic tests.
"""

from __future__ import annotations

import json
from pathlib import Path

_DEFAULT = Path.home() / ".alphaforge-anton" / "edges-trials.jsonl"


def _path(path: Path | None) -> Path:
    p = path or _DEFAULT
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _append(rec: dict, path: Path | None) -> None:
    with _path(path).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")


def _read(path: Path | None) -> list[dict]:
    p = _path(path)
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def declare_budget(edge_id: str, trials: int, path: Path | None = None) -> None:
    """Declare an edge's trial budget up front (the latest declaration is the active one)."""
    _append({"edge_id": edge_id, "kind": "budget", "n": int(trials)}, path)


def record_trial(edge_id: str, n: int = 1, path: Path | None = None) -> None:
    """Record n trials spent against an edge — appends, never edits a prior line."""
    _append({"edge_id": edge_id, "kind": "trial", "n": int(n)}, path)


def budget(edge_id: str, path: Path | None = None) -> int:
    """The active (latest-declared) trial budget for an edge; 0 if none declared."""
    decls = [r["n"] for r in _read(path) if r["edge_id"] == edge_id and r["kind"] == "budget"]
    return decls[-1] if decls else 0


def spent(edge_id: str, path: Path | None = None) -> int:
    """Total trials spent against an edge."""
    return sum(r["n"] for r in _read(path) if r["edge_id"] == edge_id and r["kind"] == "trial")


def remaining(edge_id: str, path: Path | None = None) -> int:
    """Budget minus spent — the headroom the funnel must respect before it trusts a pass."""
    return budget(edge_id, path) - spent(edge_id, path)
