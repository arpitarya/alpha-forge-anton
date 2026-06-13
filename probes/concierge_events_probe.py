"""Concierge event-protocol probe — the contract behind Orff's chat-app + Claude-
Code feature set (typed SSE events, action cards, follow-ups, vision routing,
elgar-backed memory). Standalone: no backend server, no CDP.

Run:  just probe concierge-events
"""

from __future__ import annotations

import asyncio
import sys
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


def main() -> int:
    from alphaforge_anton_llm import registry
    from alphaforge_anton_llm.providers._vision import parse_data_url
    from alphaforge_anton_llm.types import Message

    from app.modules.concierge.action_service import detect_action
    from app.modules.concierge.compose_registry import COMPOSABLE_COMPONENTS
    from app.modules.concierge.followup_service import parse_followups
    from app.modules.concierge.memory_service import load_memory, save_memory
    from app.modules.concierge.stream_events import redact, split_thinking

    # ── reasoning split (thinking event) ──
    think, vis = split_thinking("<think>weigh risk</think>Buy index funds")
    check("closed <think> splits reasoning from answer", think == "weigh risk" and vis == "Buy index funds")
    check("open <think> is all reasoning, no answer yet", split_thinking("<think>still going") == ("still going", ""))
    check("plain text passes through", split_thinking("just answer") == ("", "just answer"))

    # ── secret redaction (error event) ──
    red = redact("GET https://x/v1?api_key=SECRET&z=1 failed")
    check("api_key redacted from error", "SECRET" not in red and "<redacted>" in red)

    # ── action card (confirm event) ──
    reb = detect_action("please rebalance my equity sleeve")
    check("rebalance → action card with steps", bool(reb) and reb["action"] == "Rebalance portfolio" and len(reb["steps"]) >= 2)
    check("stable action id (no random hash)", detect_action("rebalance now")["id"] == "rebalance-portfolio")
    check("non-mutating prompt → no card", detect_action("what is xirr") is None)

    # ── follow-up chips ──
    chips = parse_followups('```json\n["Show drawdown", "Trim winners", "Export CSV", "Extra"]\n```')
    check("follow-ups parse + cap at 3", chips == ["Show drawdown", "Trim winners", "Export CSV"])
    check("bad follow-up json → []", parse_followups("not json") == [])

    # ── vision routing ──
    check("vision providers declared in manifest", registry.vision_providers() == ["gemini", "claude-sdk"])
    check("data URL parses to (mime, b64)", parse_data_url("data:image/png;base64,QUJD") == ("image/png", "QUJD"))
    check("non-image URL rejected", parse_data_url("http://x") is None)
    msg = Message(role="user", content="what's this", images=["data:image/png;base64,QUJD"])
    check("Message carries images", len(msg.images) == 1)

    # ── DiffTable in the composable vocabulary ──
    check("DiffTable is composable (plan diffs)", "DiffTable" in COMPOSABLE_COMPONENTS)

    # ── elgar-backed memory (one-repo store) ──
    from app.modules.concierge.memory_service import MEMORY_DOC_ID

    check("memory doc id is the elgar key", MEMORY_DOC_ID == "orff-context")
    check("load_memory never raises (best-effort)", isinstance(asyncio.run(load_memory()), str))

    async def _roundtrip() -> tuple[str, str, str]:
        saved = await save_memory("probe: moderate risk, 6mo buffer")
        loaded = await load_memory()
        again = await save_memory("probe: moderate risk, 6mo buffer")  # identical: must not raise
        await save_memory("")  # reset so the probe leaves no residue
        return saved, loaded, again

    saved, loaded, again = asyncio.run(_roundtrip())
    check("elgar memory save→load round-trips", saved == loaded == "probe: moderate risk, 6mo buffer")
    check("re-saving identical content does not error", again == saved)

    # ── elgar-backed conversation history (one doc per session) ──
    from app.modules.concierge.concierge_schemas import SessionMeta, SessionTurn
    from app.modules.concierge.history_service import (
        SESSION_PREFIX,
        delete_session,
        list_sessions,
        load_session,
        save_session,
    )

    check("session doc id is namespaced", SESSION_PREFIX == "orff-session-")

    async def _history() -> tuple[bool, bool, bool]:
        meta = SessionMeta(id="probe-hist", title="Probe chat")
        await save_session(
            meta, [SessionTurn(query="q1", response="a1", provider="gemini", model="flash")]
        )
        doc = await load_session("probe-hist")
        listed = any(r.id == "probe-hist" for r in await list_sessions())
        gone = await delete_session("probe-hist")  # also leaves the store clean
        absent = not any(r.id == "probe-hist" for r in await list_sessions())
        resumes = doc.turns[0].query == "q1" and doc.turns[0].response == "a1"
        return resumes, listed, (gone and absent)

    resumes, listed, removed = asyncio.run(_history())
    check("history save→load resumes its turns", resumes)
    check("saved session appears in the history list", listed)
    check("history delete removes it from the store", removed)

    print("\n" + ("❌ concierge event protocol drift" if _fail else "✅ concierge event protocol intact"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
