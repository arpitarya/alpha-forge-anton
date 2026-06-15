"""HTTP client for Parallel's Search API — isolated so `grounding_service` stays the
orchestrator (budget cap + Search/Task tagging) within the line budget.

`grounding_service` selects depth (result count + chars) per Search vs Task tier;
the true async Task API (job create + long-poll) is a follow-up — "task" mode is
currently a deeper Search call (more results, longer excerpts, higher price).
"""

from __future__ import annotations

import httpx

_API = "https://api.parallel.ai/v1beta/search"
_BETA = "search-extract-2025-10-10"
_PREAMBLE = (
    "Live web results from a Parallel deep search (ground time-sensitive facts; cite "
    "the source URL, and say so if the results don't cover the question):\n\n"
)


async def search(key: str, query: str, *, limit: int = 5, max_chars: int = 600) -> list[dict]:
    headers = {"x-api-key": key, "parallel-beta": _BETA, "Content-Type": "application/json"}
    payload = {
        "objective": query,
        "search_queries": [query],
        "max_results": limit,
        "max_chars_per_result": max_chars,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(_API, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json().get("results", [])


def format_results(results: list[dict]) -> str:
    lines = [
        f"- {r.get('title', '')} ({r.get('url', '')})\n  {' '.join(r.get('excerpts', []))[:600]}"
        for r in results
    ]
    return _PREAMBLE + "\n".join(lines)
