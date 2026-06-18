"""Parallel web grounding for Orff — the shared "Deep search" executor (handoff §9).

``run`` does one Parallel call (key-gated, fail-open) and records a tagged Cage
receipt; ``budget_status`` reads month-to-date Parallel spend vs the strategy-config
cap (INR). Both are called by ``deep_search_service`` (the agent-initiated, confirm-
gated flow) — there is no always-on inject path. Guardrails:

- **Hard monthly budget cap.** ``budget_status`` compares month-to-date Parallel
  spend (Cage ledger, INR) to ``parallel.monthly_budget_inr``; over budget ⇒ the
  flow degrades to the free sources. No call, no receipt.
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

from app.modules.brokers.fx import to_inr
from app.modules.concierge import parallel_client
from app.modules.signals.strategy_config import load_config

logger = logging.getLogger(__name__)

# Per-call price → the Cage receipt (drives the budget). Pinned to Parallel's
# published rates: Search = $0.005/req; Task pinned to the `core` processor
# ($0.025/run). When the real Task API lands it MUST use `core` to match this.
_TASK_PROCESSOR = "core"
_SEARCH_USD, _TASK_USD = 0.005, 0.025
_DEEP = ("deep dive", "deep-dive", "deep research", "thorough research")


@dataclass
class Grounding:
    text: str
    detail: str
    ms: int


def kind(prompt: str, allow_task: bool) -> str:
    """Pick the Parallel tier: Task only on a deep-dive prompt when allowed, else Search."""
    return "task" if allow_task and any(d in prompt.lower() for d in _DEEP) else "search"


def budget_status() -> tuple[int, int, bool]:
    """Month-to-date Parallel spend, the monthly cap, and whether we're over (all INR)."""
    cfg = load_config()
    budget = round(cfg.parallel.monthly_budget_inr)
    mtd = round(to_inr(cage_meter.month_spend_usd("parallel"), "USD"))
    return mtd, budget, budget > 0 and mtd >= budget


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
