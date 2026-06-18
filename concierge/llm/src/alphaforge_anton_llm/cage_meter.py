"""Cage metering adapter — record every completion's spend into the Cage ledger.

Cage is the sibling *flux* (``~/my_programs/cage``): a deterministic LLM-cost
ledger. Orff is its first integration point — the gateway records each
``ProviderResponse`` right where cost is already known (cage-plan §2, §5).

Fail-open by construction: if cage is not installed or anything raises, metering
is a silent no-op. The meter must never sit in a completion's failure path.
"""

from __future__ import annotations

import datetime as _dt
import logging
from pathlib import Path

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.types import ProviderResponse, QueryType

logger = logging.getLogger(__name__)

# The .cage/ ledger lives at the Anton repo root (see docs/cage.md).
_ROOT = Path(__file__).resolve().parents[4]


def record(
    resp: ProviderResponse,
    *,
    query_type: QueryType,
    latency_ms: int = 0,
    session: str = "",
    task: str = "",
) -> None:
    """Append one call row to the Cage ledger. Never raises."""
    try:
        import cage
    except ImportError:
        return
    try:
        # Cache-aware: prompt_tokens is the uncached remainder; cache reads bill ~0.1x
        # and cache writes ~1.25x. `cached_in` records the served-from-cache split.
        cost = pricing.estimate_cost_usd(
            resp.provider, resp.model, resp.prompt_tokens, resp.completion_tokens,
            cache_read=resp.cache_read_input_tokens,
            cache_creation=resp.cache_creation_input_tokens,
        )
        cage.record_call(
            route=query_type.value,
            provider=resp.provider,
            model=resp.model,
            tokens_in=resp.prompt_tokens + resp.cache_creation_input_tokens,
            tokens_out=resp.completion_tokens,
            cached_in=resp.cache_read_input_tokens,
            est_cost_usd=cost,
            agent="orff",
            latency_ms=latency_ms,
            session=session,
            task=task,
            root=_ROOT,
        )
    except Exception as exc:  # pragma: no cover — metering is best-effort
        logger.debug("cage metering skipped: %s", exc)


def record_tool(
    *,
    route: str,
    provider: str,
    est_cost_usd: float,
    latency_ms: int = 0,
    session: str = "",
    task: str = "",
) -> None:
    """Append one non-LLM tool call (e.g. a Parallel web search) to the ledger.

    Same fail-open contract as ``record``: a search carries no tokens, so spend is
    the caller's per-call price. Lets the SessionMeter show real (paid) tool spend
    beside LLM spend. Never raises.
    """
    try:
        import cage
    except ImportError:
        return
    try:
        cage.record_call(
            route=route,
            provider=provider,
            model="search",
            tokens_in=0,
            tokens_out=0,
            est_cost_usd=est_cost_usd,
            agent="orff",
            latency_ms=latency_ms,
            session=session,
            task=task,
            root=_ROOT,
        )
    except Exception as exc:  # pragma: no cover — metering is best-effort
        logger.debug("cage tool metering skipped: %s", exc)


def month_spend_usd(provider: str) -> float:
    """Calendar month-to-date USD spend for a provider, read from the Cage ledger.

    Powers the Parallel hard budget cap (§9). Fail-open: cage absent / no ledger /
    any error → 0.0 (a missing ledger means no recorded spend anyway).
    """
    try:
        from cage import ledger
    except ImportError:
        return 0.0
    try:
        month = _dt.datetime.now(_dt.UTC).strftime("%Y-%m")
        return sum(
            row.get("est_cost_usd", 0.0)
            for row in ledger.calls(_ROOT)
            if row.get("provider") == provider and (row.get("ts") or "")[:7] == month
        )
    except Exception as exc:  # pragma: no cover — best-effort
        logger.debug("cage month spend read skipped: %s", exc)
        return 0.0
