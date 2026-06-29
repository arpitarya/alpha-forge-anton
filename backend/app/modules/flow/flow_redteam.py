"""The red-team service — the ONLY LLM call in the flow, cage-metered by the gateway.

`create_gateway().complete()` auto-records the spend to the cage ledger, so this stage is
metered by construction. It is OFF the deterministic path: the funnel/cone/sizing never
import this module; it only critiques numbers handed to it. Generation runs as a background
job (never blocking) and the result is cached per edge so re-viewing doesn't re-bill the LLM.
"""

from __future__ import annotations

import asyncio
import json
import re

from alphaforge_anton_llm.gateway import create_gateway
from alphaforge_anton_llm.types import Message, QueryType

from app.modules.flow.flow_redteam_prompt import build_messages
from app.modules.flow.flow_redteam_schema import (
    RedteamContext,
    RedteamObjection,
    RedteamReport,
    Severity,
)
from app.modules.flow.flow_run_schema import RunPhase

_gateway = create_gateway()
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
_RANK = {Severity.HIGH: 0, Severity.MED: 1, Severity.LOW: 2}
_CACHE: dict[str, RedteamReport] = {}  # edge_id → latest report (cached: LLM costs money)


def get(edge_id: str) -> RedteamReport | None:
    return _CACHE.get(edge_id)


def _parse(text: str, provider: str, model: str) -> RedteamReport:
    m = _FENCE.search(text)
    data = json.loads(m.group(1) if m else text)
    objs = [RedteamObjection(**o) for o in data.get("objections", [])]
    objs.sort(key=lambda o: _RANK.get(o.severity, 1))  # loudest risk leads
    return RedteamReport(
        phase=RunPhase.DONE,
        objections=objs,
        tenth_man=data.get("tenth_man", ""),
        runner_ups=data.get("runner_ups", []),
        tripwires=data.get("tripwires", []),
        provider=provider,
        model=model,
    )


async def _complete(messages: list[Message]) -> RedteamReport:
    r = await _gateway.complete(messages, query_type=QueryType.INVESTMENT_PLAN)
    try:
        return _parse(r.content, r.provider, r.model)
    except (ValueError, TypeError):  # JSONDecodeError is a ValueError — one repair round, then fail
        fix = [
            *messages,
            Message(role="assistant", content=r.content),
            Message(role="user", content="That was not valid JSON. Return ONLY the JSON object."),
        ]
        r2 = await _gateway.complete(fix, query_type=QueryType.INVESTMENT_PLAN)
        return _parse(r2.content, r2.provider, r2.model)


async def _execute(ctx: RedteamContext) -> None:
    _CACHE[ctx.edge_id] = RedteamReport(phase=RunPhase.RUNNING)
    try:
        _CACHE[ctx.edge_id] = await _complete(build_messages(ctx))
    except Exception as e:  # never crash the loop; surface the failure honestly
        _CACHE[ctx.edge_id] = RedteamReport(phase=RunPhase.FAILED, error=str(e))


def start(ctx: RedteamContext) -> RedteamReport:
    """Start (or rejoin) the red-team for an edge — cached; no double-run while in flight."""
    cur = _CACHE.get(ctx.edge_id)
    if cur is not None and cur.phase in (RunPhase.QUEUED, RunPhase.RUNNING):
        return cur
    _CACHE[ctx.edge_id] = RedteamReport(phase=RunPhase.QUEUED)
    asyncio.create_task(_execute(ctx))  # noqa: RUF006 — cache holds the report, not the task
    return _CACHE[ctx.edge_id]
