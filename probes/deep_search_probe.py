"""Deep-search probe — the agent-initiated, confirm-gated "Deep search" flow.

Standalone (no CDP, no network, no key): stubs the Parallel HTTP client + the Cage
meter (record + month-to-date spend), then drives deep_search_service + the tool
loop. Asserts every docs/deep-search-ask.handoff.md §Acceptance row:

  - Auto        → request_deep_search confirm card (reasons + cost), NO Parallel call
  - Confirm     → one Parallel call + one Cage receipt, results returned
  - Reject      → building the card makes zero calls
  - Always      → grounding runs cardless and reaches the answer (no confirm)
  - Never       → the tool is not offered; never asked, never called
  - Over budget → card/flow degrades to free sources, no call, no receipt

Run:  just probe deep-search
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from alphaforge_anton_llm import cage_meter

from app.modules.concierge import deep_search_service as ds
from app.modules.concierge import grounding_service, parallel_client
from app.modules.concierge.tool_layer import run as tool_run
from app.modules.concierge.tool_registry import DEEP_SEARCH_TOOL, trusted_schemas

_fail = 0
_spy = {"parallel": 0, "cage": 0}
_mtd_usd = {"v": 0.0}  # stubbed month-to-date Parallel spend (USD)


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


async def _fake_search(key, query, *, limit=5, max_chars=600) -> list[dict]:
    _spy["parallel"] += 1
    return [{"title": "PARAS order win", "url": "https://x.test", "excerpts": ["big order"]}]


def _reset() -> None:
    _spy.update(parallel=0, cage=0)


def _assembled(mode: str) -> MagicMock:
    a = MagicMock()
    a.preferred, a.confirmed, a.msgs, a.model, a.deep_search_mode = "claude-sdk", True, [], "m", mode
    return a


# Compact fake Anthropic response classes (mirror concierge_tools_probe).
class _U:
    input_tokens = 10
    output_tokens = 5


class _DSTb:
    type = "tool_use"
    id = "d1"
    name = DEEP_SEARCH_TOOL
    input = {"reasons": "Need live PARAS news past my cutoff", "queries": ["PARAS defence order 2026"]}


class _FT:
    type = "text"
    text = "Here is the latest."


class _RTool:
    content = [_DSTb()]
    usage = _U()


class _RFinal:
    content = [_FT()]
    usage = _U()


async def _run() -> None:
    parallel_client.search = _fake_search                                  # no network / key
    cage_meter.record_tool = lambda **kw: _spy.update(cage=_spy["cage"] + 1)
    cage_meter.month_spend_usd = lambda provider: _mtd_usd["v"]
    os.environ["PARALLEL_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "k"

    # ── confirm_card: Auto card payload + Reject (no call) ──────────────────
    _reset()
    _mtd_usd["v"] = 0.0
    card = ds.confirm_card("Need live data", ["q1", "q2"])
    check("card summary = reasons", card["summary"] == "Need live data")
    check("card steps = queries", card["steps"] == ["q1", "q2"])
    check("card detail has cost + budget", "~₹0.5" in card["detail"] and "of ₹" in card["detail"])
    check("card apply → /deep-search", card.get("apply", {}).get("path") == "/api/v1/concierge/deep-search")
    check("reject — building the card makes no call", _spy["parallel"] == 0 and _spy["cage"] == 0)

    # ── Confirm path: run() → one Parallel call + one Cage receipt ──────────
    _reset()
    text = await ds.run(["PARAS defence order 2026"])
    check("confirm → exactly one Parallel call", _spy["parallel"] == 1, str(_spy))
    check("confirm → exactly one Cage receipt", _spy["cage"] == 1, str(_spy))
    check("confirm → grounded text returned", "PARAS order win" in text, text[:60])

    # ── Auto via the tool loop: confirm event, NO Parallel call ─────────────
    _reset()
    mc = MagicMock(); mc.messages.create = AsyncMock(return_value=_RTool())
    with patch("anthropic.AsyncAnthropic", return_value=mc):
        evts, resp = await tool_run(_assembled("auto"), None)
    confirms = [e for e in evts if "confirm" in e]
    check("Auto → one confirm event", len(confirms) == 1, str(evts))
    check("Auto → confirm carries reasons", confirms and confirms[0]["confirm"]["summary"].startswith("Need live"))
    check("Auto → makes NO Parallel call", _spy["parallel"] == 0, str(_spy))
    check("Auto → loop paused for confirm", resp is not None)

    # ── Always via the tool loop: cardless run, results reach the answer ────
    _reset()
    mc2 = MagicMock(); mc2.messages.create = AsyncMock(side_effect=[_RTool(), _RFinal()])
    with patch("anthropic.AsyncAnthropic", return_value=mc2):
        evts2, resp2 = await tool_run(_assembled("always"), None)
    second_msgs = json.dumps(mc2.messages.create.call_args_list[1].kwargs["messages"], default=str)
    check("Always → no confirm event", not any("confirm" in e for e in evts2), str(evts2))
    check("Always → one Parallel call + receipt", _spy["parallel"] == 1 and _spy["cage"] == 1, str(_spy))
    check("Always → grounding reaches the answer", "PARAS order win" in second_msgs)
    check("Always → final answer produced", resp2 is not None and "latest" in resp2.content)

    # ── Never: tool not offered, never asked / called ──────────────────────
    _reset()
    offered = [t.name for t in trusted_schemas(offer_deep_search=False)]
    check("Never → request_deep_search not offered", DEEP_SEARCH_TOOL not in offered)
    check("Auto/Always → request_deep_search offered", DEEP_SEARCH_TOOL in [t.name for t in trusted_schemas()])
    mc3 = MagicMock(); mc3.messages.create = AsyncMock(return_value=_RFinal())
    with patch("anthropic.AsyncAnthropic", return_value=mc3):
        evts3, _ = await tool_run(_assembled("never"), None)
    tools_sent = [t["name"] for t in mc3.messages.create.call_args.kwargs["tools"]]
    check("Never → tool absent from the offered set", DEEP_SEARCH_TOOL not in tools_sent)
    check("Never → no confirm, no Parallel call", not any("confirm" in e for e in evts3) and _spy["parallel"] == 0)

    # ── Over budget: card degrades, run skips (no call, no receipt) ─────────
    _reset()
    _mtd_usd["v"] = 1000.0  # ≫ the ₹ monthly budget once converted
    over_card = ds.confirm_card("Need live data", ["q1"])
    check("over budget → card says budget used", "budget used" in over_card["detail"].lower())
    check("over budget → card has no apply target", "apply" not in over_card)
    note = await ds.run(["q1"])
    check("over budget → run skips the call", _spy["parallel"] == 0 and _spy["cage"] == 0, str(_spy))
    check("over budget → run degrades to free sources", "free sources" in note.lower())


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ deep-search flow FAILED" if _fail else "✅ Agent-initiated deep-search flow holds"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
