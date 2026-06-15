"""Parallel web-grounding probe — verifies the §9 opt-in "Deep search" wiring.

Standalone (no CDP, no network, no key): stubs the Parallel HTTP client + the Cage
meter (record + month-to-date spend), then drives grounding_service.inject. Asserts
the handoff §9 acceptance conditions:

  - flag OFF                 → no Parallel call, no Cage receipt, no ToolTrail step
  - flag ON + key + budget   → one call + one Cage receipt + one `parallel` step
  - flag ON + key MISSING    → fail-open: no call, no receipt
  - flag ON + OVER BUDGET    → call skipped (no call, no receipt) + a "skipped" note

Run:  just probe parallel-grounding
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from alphaforge_anton_llm import cage_meter

from app.modules.concierge import grounding_service as g
from app.modules.concierge import parallel_client
from app.modules.concierge.concierge_schemas import ChatMessage, ChatRequest

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


async def _inject(web_grounding: bool) -> tuple[list, list[dict]]:
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="latest on PARAS defence order")],
        web_grounding=web_grounding,
    )
    msgs: list = []
    trace: list[dict] = []
    await g.inject(req, msgs, trace)
    return msgs, trace


async def _run() -> None:
    parallel_client.search = _fake_search                       # no real network / key
    cage_meter.record_tool = lambda **kw: _spy.update(cage=_spy["cage"] + 1)  # spy receipt
    cage_meter.month_spend_usd = lambda provider: _mtd_usd["v"]  # control the budget

    _reset()
    _mtd_usd["v"] = 0.0
    os.environ["PARALLEL_API_KEY"] = "test-key"
    msgs, trace = await _inject(web_grounding=False)
    check("flag OFF → no Parallel call", _spy["parallel"] == 0)
    check("flag OFF → no Cage receipt", _spy["cage"] == 0)
    check("flag OFF → no trace step", not trace and not msgs)

    _reset()
    msgs, trace = await _inject(web_grounding=True)
    steps = [s for s in trace if s["name"] == "parallel"]
    check("flag ON → exactly one Parallel call", _spy["parallel"] == 1, str(_spy))
    check("flag ON → exactly one Cage receipt", _spy["cage"] == 1, str(_spy))
    check("flag ON → one `parallel` ToolTrail step", len(steps) == 1, str(trace))
    check("flag ON → grounding system message injected",
          any("Parallel deep search" in m.content for m in msgs))

    _reset()
    os.environ.pop("PARALLEL_API_KEY", None)
    msgs, trace = await _inject(web_grounding=True)
    check("flag ON + no key → fail-open (no call)", _spy["parallel"] == 0)
    check("flag ON + no key → no receipt, no step", _spy["cage"] == 0 and not trace)

    _reset()
    os.environ["PARALLEL_API_KEY"] = "test-key"
    _mtd_usd["v"] = 1000.0  # ≫ the ₹ monthly budget once converted
    msgs, trace = await _inject(web_grounding=True)
    skipped = [s for s in trace if s["name"] == "parallel" and "skipped" in s["detail"]]
    check("over budget → Parallel call skipped", _spy["parallel"] == 0, str(_spy))
    check("over budget → no Cage receipt", _spy["cage"] == 0)
    check("over budget → one `skipped` note + step", len(skipped) == 1 and bool(msgs), str(trace))


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ grounding wiring FAILED" if _fail else "✅ Parallel grounding wiring holds"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
