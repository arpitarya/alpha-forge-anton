"""Dedicated free-cash endpoints — snapshot + per-broker sync.

Separate from /portfolio/wallets (which bundles holdings + cash together).
These routes are fast-path: GET returns cached state; POST /sync triggers
the CDP/API round-trip only for cash-capable brokers.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.modules.brokers.registry import SOURCES
from app.modules.brokers.wallet_aggregator import list_wallets, sync_all, sync_one

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger("routes.cash")

_DISCLAIMER = "Not SEBI registered investment advice."


def _as_cash(w) -> dict:  # type: ignore[no-untyped-def]
    d = w.model_dump(mode="json")
    d["source"] = d.pop("slug")
    return d


@router.get("")
async def get_cash():
    """Cached free-cash state — no sync triggered, always instant."""
    cash = [_as_cash(w) for w in list_wallets() if w.supports_cash]
    return {"cash": cash, "disclaimer": _DISCLAIMER}


@router.post("/sync")
async def sync_all_cash():
    """Sync all cash-capable brokers concurrently (CDP + HTTP).

    Zerodha uses enctoken over HTTP (~1 s).
    Groww and Angel One open a fresh CDP tab (~15–25 s each).
    """
    refreshed = await sync_all()
    cash = [
        _as_cash(w)
        for slug, w in refreshed.items()
        if getattr(SOURCES.get(slug), "supports_cash", False)
    ]
    return {"cash": cash, "disclaimer": _DISCLAIMER}


@router.post("/{slug}/sync")
async def sync_one_cash(slug: str):
    """Sync free-cash for a single broker."""
    if slug not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {slug!r}")
    if not getattr(SOURCES[slug], "supports_cash", False):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"{slug!r} does not support cash fetching.",
        )
    try:
        wallet = await sync_one(slug)
    except Exception as e:
        logger.exception("Cash sync failed for %s", slug)
        raise HTTPException(400, f"Cash sync failed: {e}") from e
    return {"cash": _as_cash(wallet), "disclaimer": _DISCLAIMER}
