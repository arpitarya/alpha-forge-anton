"""Sync investment-related Claude Code chats into Orff's history (elgar `sessions/`).

A re-runnable mechanism (`just sync-claude-history [--dry-run]`): scan the local
Claude Code transcripts under `~/.claude/projects`, keep the conversations that talk
about investing (keyword filter on what the human actually asked), and upsert each as
a clean transcript into the elgar `sessions/` collection — the same store Orff's
History panel reads. Idempotent: a stable id per Claude session + a deterministic
render (the transcript's mtime as `updated`) means a re-run only commits what changed.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

from app.modules.concierge.claude_parse import parse
from app.modules.concierge.concierge_schemas import SessionMeta, SessionTurn
from app.modules.concierge.history_service import SESSION_DIR, render_session
from app.modules.plans import elgar_bridge

PROJECTS = Path(os.environ.get("CLAUDE_PROJECTS", Path.home() / ".claude" / "projects"))
MIN_HITS = 2  # min distinct investment keywords in the human's prompts to qualify
_KEYWORDS = (
    "portfolio", "holding", "equity", "mutual fund", "sip", "allocation", "rebalanc",
    "asset class", "drawdown", "xirr", "cagr", "dividend", "valuation", "net worth",
    "emergency fund", "invest", "stock", "nifty", "sensex", "gold", "crypto", "bond",
    "fixed deposit", "capital gain", "retire", "corpus", "broker", "holdings",
)


def is_investment(turns: list[dict]) -> bool:
    asked = " ".join(t["query"] for t in turns).lower()
    return sum(k in asked for k in _KEYWORDS) >= MIN_HITS


def _doc_id(path: Path) -> str:
    return f"claude-{path.stem}"


def _mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(timespec="seconds")


async def sync(dry_run: bool = False) -> dict:
    transcripts = sorted(PROJECTS.glob("*/*.jsonl"))
    matched = 0
    for path in transcripts:
        title, turns = parse(path)
        if not turns or not is_investment(turns):
            continue
        matched += 1
        meta = SessionMeta(id=_doc_id(path), title=title)
        if dry_run:
            print(f"  ✓ {meta.id}  ({len(turns)} turns)  {title[:70]}")
            continue
        body = render_session(
            meta, [SessionTurn(**t) for t in turns], updated=_mtime(path), source="claude-code"
        )
        msg = f"sync: claude {meta.id}"
        await elgar_bridge.save(meta.id, body, message=msg, collection=SESSION_DIR)
    return {"scanned": len(transcripts), "matched": matched}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="preview matches, write nothing")
    a = ap.parse_args()
    res = asyncio.run(sync(a.dry_run))
    tail = "(dry run — nothing written)" if a.dry_run else "→ elgar sessions/"
    print(f"\nscanned {res['scanned']} transcripts · {res['matched']} investment chats {tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
