"""Opt-in Parallel web grounding for Orff — the "Deep search" path (handoff §9).

When a request sets ``web_grounding`` this calls Parallel, injects the ranked
extracts as a grounding block, and adds a ``parallel`` ToolTrail step. Guardrails:

- **Hard monthly budget cap.** Before any call it reads month-to-date Parallel
  spend from the Cage ledger and compares it (INR) to ``parallel.monthly_budget_inr``
  in the strategy config; over budget ⇒ the call is **skipped** and Orff is told to
  answer from the free sources. No call, no receipt.
- **Search vs Task.** A deep-dive prompt uses the costlier Task tier — but only when
  ``parallel.allow_task_api`` is set; the Cage receipt is tagged ``grounding-{kind}``.
- **Key** from the afbach vault (``PARALLEL_API_KEY``, boot-injected — never env/code;
  guarded by probes/parallel_keys_probe.py). Fail-open: any error → free path.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

from alphaforge_anton_llm import cage_meter
from alphaforge_anton_llm.types import Message

from app.modules.brokers.fx import to_inr
from app.modules.concierge import parallel_client
from app.modules.concierge.concierge_schemas import ChatRequest
from app.modules.signals.strategy_config import load_config

logger = logging.getLogger(__name__)

_SEARCH_USD, _TASK_USD = 0.01, 0.10  # per-call price → the Cage receipt (drives the budget)
_DEEP = ("deep dive", "deep-dive", "deep research", "thorough research")


@dataclass
class Grounding:
    text: str
    detail: str
    ms: int


def _kind(prompt: str, allow_task: bool) -> str:
    return "task" if allow_task and any(d in prompt.lower() for d in _DEEP) else "search"


async def run(query: str, *, kind: str = "search") -> Grounding | None:
    """One Parallel call (key-gated, fail-open); records a tagged Cage receipt."""
    key = os.getenv("PARALLEL_API_KEY")
    if not key or not query.strip():
        return None
    limit, chars, price = (10, 1500, _TASK_USD) if kind == "task" else (5, 600, _SEARCH_USD)
    t = time.perf_counter()
    try:
        results = await parallel_client.search(key, query, limit=limit, max_chars=chars)
    except Exception as exc:  # grounding is best-effort — never block the chat
        logger.warning("parallel grounding failed: %s", exc)
        return None
    ms = int((time.perf_counter() - t) * 1000)
    if not results:
        return None
    cage_meter.record_tool(
        route=f"grounding-{kind}", provider="parallel", est_cost_usd=price, latency_ms=ms
    )
    return Grounding(parallel_client.format_results(results), f"{kind}: {len(results)} results", ms)


async def inject(req: ChatRequest, msgs: list[Message], trace: list[dict]) -> None:
    """Append a Parallel grounding block + trace step when opted in and under budget."""
    if not req.web_grounding:
        return
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    if not last_user:
        return
    cfg = load_config()
    budget = round(cfg.parallel.monthly_budget_inr)
    mtd = round(to_inr(cage_meter.month_spend_usd("parallel"), "USD"))
    if budget > 0 and mtd >= budget:
        msgs.append(
            Message(
                role="system",
                content=(
                    f"Parallel deep-search budget for this month is used (₹{mtd} of ₹{budget}) — "
                    "answer from the free sources and say so."
                ),
            )
        )
        trace.append({"name": "parallel", "detail": f"budget ₹{mtd}/₹{budget} — skipped", "ms": 0})
        return
    g = await run(last_user, kind=_kind(last_user, cfg.parallel.allow_task_api))
    if not g:
        return
    msgs.append(Message(role="system", content=g.text))
    trace.append({"name": "parallel", "detail": g.detail, "ms": g.ms})
