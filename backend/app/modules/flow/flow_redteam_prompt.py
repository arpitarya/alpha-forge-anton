"""Builds the red-team messages — a two-tier critique grounded in deterministic evidence.

The system prompt fixes the job: critique the EVIDENCE, never recompute a number, and
return strict JSON. Tier 1 is an evidence critic (severity-tagged objections about the
stats); tier 2 is a forced 10th-Man dissent — the strongest case AGAINST proceeding even
if everything looks clean. Plus runner-ups (alternatives) and tripwires (live invalidators).
"""

from __future__ import annotations

import json

from alphaforge_anton_llm.types import Message

from app.modules.flow.flow_redteam_schema import RedteamContext

_SCHEMA = (
    '{"objections": [{"severity": "high|med|low", "title": "...", "detail": "..."}], '
    '"tenth_man": "...", "runner_ups": ["..."], "tripwires": ["..."]}'
)

_SYSTEM = (
    "You are the RED-TEAM for a quant trading edge — a hostile, evidence-first critic whose job "
    "is to find what is WRONG, not to cheerlead. You are given a pre-registered edge that already "
    "PASSED a deterministic funnel. Two tiers:\n"
    "  1) EVIDENCE CRITIC — scrutinise the statistics handed to you (overfitting probability, "
    "deflated Sharpe, the multiple-testing haircut, walk-forward consistency, the worst-case cone, "
    "the position size). Raise concrete objections, each tagged high/med/low severity.\n"
    "  2) 10th-MAN — even if every number looks clean, you MUST argue the single strongest case "
    "AGAINST deploying (regime change, crowding, structural break, a hidden assumption).\n"
    "Then list runner-ups (alternatives worth preferring) and tripwires (live conditions that "
    "would invalidate the edge).\n"
    "HARD RULES: do NOT invent or recompute any number — reason only about the evidence given. "
    f"Return STRICT JSON, no prose, exactly this shape:\n{_SCHEMA}"
)


def _evidence(ctx: RedteamContext) -> str:
    return json.dumps(ctx.model_dump(), indent=2)


def build_messages(ctx: RedteamContext) -> list[Message]:
    """System critic instructions + the deterministic evidence as the user turn."""
    user = (
        f"Edge {ctx.edge_id} — hypothesis: {ctx.hypothesis or '(none given)'}.\n"
        f"Deterministic evidence (already computed; critique it, do not recompute):\n"
        f"{_evidence(ctx)}"
    )
    return [Message(role="system", content=_SYSTEM), Message(role="user", content=user)]
