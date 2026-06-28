"""Edge-library read side — aggregate jsonl + tolerate the legacy markdown-only entry.

The journal mixes a structured `journal.jsonl` mirror with older markdown-only docs
(each embedding its record as a ```json block). `library_summary` must read both,
dedupe by (edge_id, run_at), and group by edge so one edge tested many times counts
once — reproducing the real "1 tested · 1 killed · 0 live · 100% kill-rate" state.

    uv run pytest tests/test_edge_library.py -v
"""

from __future__ import annotations

from app.modules.edges import edge_journal, edge_library

_MD = """---
edge: edge-001
verdict: KILL
---
# KILL — edge-001

```json
{"edge_id": "edge-001", "run_at": "2026-06-27T18:13:49+00:00", "gate_reached": 0, "passed": false}
```
"""


def _point_journal(tmp_path, monkeypatch):
    path = tmp_path / "edges-journal" / "journal.jsonl"
    path.parent.mkdir(parents=True)
    monkeypatch.setattr(edge_library, "jsonl_path", lambda: path)
    return path


def test_empty_journal_is_all_zeros(tmp_path, monkeypatch):
    _point_journal(tmp_path, monkeypatch)
    s = edge_library.library_summary()
    assert (s.tested, s.killed, s.passed, s.live, s.kill_rate) == (0, 0, 0, 0, 0.0)


def test_markdown_only_kill_is_counted(tmp_path, monkeypatch):
    path = _point_journal(tmp_path, monkeypatch)
    (path.parent / "edge-001-20260627T181349.md").write_text(_MD)
    s = edge_library.library_summary()
    assert s.tested == 1 and s.killed == 1 and s.passed == 0 and s.live == 0
    assert s.kill_rate == 1.0
    assert s.recent[0].edge_id == "edge-001" and s.recent[0].verdict == "KILL"


def test_repeated_runs_group_by_edge_latest_wins(tmp_path, monkeypatch):
    path = _point_journal(tmp_path, monkeypatch)
    early = edge_journal.JournalRecord(edge_id="edge-2", run_at="2026-06-01T00:00:00+00:00")
    late = edge_journal.JournalRecord(
        edge_id="edge-2", run_at="2026-06-10T00:00:00+00:00", passed=True, gate_reached=2)
    path.write_text(early.model_dump_json() + "\n" + late.model_dump_json() + "\n")
    s = edge_library.library_summary()
    assert s.tested == 1 and s.passed == 1 and s.killed == 0  # latest PASS wins
    assert s.kill_rate == 0.0


def test_jsonl_and_markdown_dedupe_same_run(tmp_path, monkeypatch):
    path = _point_journal(tmp_path, monkeypatch)
    rec = edge_journal.JournalRecord(edge_id="edge-001", run_at="2026-06-27T18:13:49+00:00")
    path.write_text(rec.model_dump_json() + "\n")
    (path.parent / "edge-001-20260627T181349.md").write_text(_MD)  # same (edge, run_at)
    s = edge_library.library_summary()
    assert s.tested == 1 and s.killed == 1  # not double-counted
