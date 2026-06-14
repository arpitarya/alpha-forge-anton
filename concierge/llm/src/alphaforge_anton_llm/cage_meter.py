"""Cage metering adapter — record every completion's spend into the Cage ledger.

Cage is the sibling *flux* (``~/my_programs/cage``): a deterministic LLM-cost
ledger. Orff is its first integration point — the gateway records each
``ProviderResponse`` right where cost is already known (cage-plan §2, §5).

Fail-open by construction: if cage is not installed or anything raises, metering
is a silent no-op. The meter must never sit in a completion's failure path.
"""

from __future__ import annotations

import logging
from pathlib import Path

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.types import ProviderResponse, QueryType

logger = logging.getLogger(__name__)

# The .cage/ ledger lives at the Anton repo root (see docs/cage.md).
_ROOT = Path(__file__).resolve().parents[4]


def record(
    resp: ProviderResponse, *, query_type: QueryType, latency_ms: int = 0,
    session: str = "", task: str = "",
) -> None:
    """Append one call row to the Cage ledger. Never raises."""
    try:
        import cage
    except ImportError:
        return
    try:
        cost = pricing.estimate_cost_usd(
            resp.provider, resp.model, resp.prompt_tokens, resp.completion_tokens
        )
        cage.record_call(
            route=query_type.value, provider=resp.provider, model=resp.model,
            tokens_in=resp.prompt_tokens, tokens_out=resp.completion_tokens,
            est_cost_usd=cost, agent="orff", latency_ms=latency_ms,
            session=session, task=task, root=_ROOT,
        )
    except Exception as exc:  # pragma: no cover — metering is best-effort
        logger.debug("cage metering skipped: %s", exc)
