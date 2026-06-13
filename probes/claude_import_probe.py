"""Claude-history sync probe — the parse + filter + render contract behind
`just sync-claude-history`. Standalone: writes a fixture transcript to a temp file,
never touches the real ~/.claude or the elgar store.

Run:  just probe claude-import
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "concierge" / "llm" / "src"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _fixture() -> list[str]:
    """A transcript with prose, an ai-title, and tool/system noise that must be dropped."""
    return [
        json.dumps({"type": "ai-title", "sessionId": "x", "aiTitle": "Rebalance my equity sleeve"}),
        json.dumps({"type": "user", "message": {"role": "user",
                    "content": [{"type": "text", "text": "Should I rebalance my portfolio toward more equity?"}]}}),
        json.dumps({"type": "user", "message": {"role": "user",
                    "content": [{"type": "text", "text": "<system-reminder>injected ctx</system-reminder>"}]}}),
        json.dumps({"type": "assistant", "message": {"role": "assistant", "model": "anthropic/claude-opus-4-8",
                    "content": [{"type": "text", "text": "Your equity is under target; add on the next SIP."},
                                {"type": "tool_use", "name": "Read", "input": {}}]}}),
        json.dumps({"type": "user", "message": {"role": "user",
                    "content": [{"type": "tool_result", "content": "file bytes"}]}}),
    ]


def main() -> int:
    from app.modules.concierge.claude_import import MIN_HITS, is_investment
    from app.modules.concierge.claude_parse import parse
    from app.modules.concierge.concierge_schemas import SessionMeta, SessionTurn
    from app.modules.concierge.history_service import _TURNS_RE, render_session

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "sess.jsonl"
        p.write_text("\n".join(_fixture()), encoding="utf-8")
        title, turns = parse(p)

    # ── clean extraction ──
    check("title comes from the ai-title record", title == "Rebalance my equity sleeve")
    check("one clean turn (system-reminder + tool_result dropped)", len(turns) == 1, f"got {len(turns)}")
    check("user prompt is the real typed text", turns[0]["query"].startswith("Should I rebalance"))
    check("assistant prose kept, tool_use dropped", turns[0]["response"].startswith("Your equity"))
    check("turn is tagged as a claude-code import", turns[0]["provider"] == "claude-code")
    check("model id shortened", turns[0]["model"] == "claude-opus-4-8")

    # ── investment keyword filter ──
    check(f"investment chat matches (≥{MIN_HITS} keywords)", is_investment(turns))
    chit = [{"query": "what's the weather like tomorrow?", "response": "sunny"}]
    check("non-investment chat is filtered out", not is_investment(chit))

    # ── deterministic, resumable render ──
    meta = SessionMeta(id="claude-x", title=title)
    sts = [SessionTurn(**t) for t in turns]
    a = render_session(meta, sts, updated="2026-06-14T00:00:00+00:00", source="claude-code")
    b = render_session(meta, sts, updated="2026-06-14T00:00:00+00:00", source="claude-code")
    check("render is deterministic (same input → same bytes)", a == b)
    check("provenance recorded in frontmatter", "source: claude-code" in a)
    m = _TURNS_RE.search(a)
    check("turns block round-trips for resume", bool(m) and json.loads(m.group(1))[0]["query"].startswith("Should I"))

    print("\n" + ("❌ claude-import contract drift" if _fail else "✅ claude-import contract intact"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
