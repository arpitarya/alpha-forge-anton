"""Aggregated portfolio endpoints — holdings, treemap, rebalance, plus mounted broker routes."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.core.logging import get_logger
from app.modules.brokers import SOURCES, HoldingsAggregator
from app.modules.brokers.brokers_routes import router as sources_router
from app.modules.brokers.cash_routes import router as cash_router
from app.modules.brokers.fx import _TTL_SECONDS as _FX_TTL_SECONDS
from app.modules.brokers.fx import get_inr_per_usd
from app.modules.brokers.dump_utils import clear_csv_cache
from app.modules.brokers.wallet_aggregator import list_wallets, sync_all, sync_one

router = APIRouter(dependencies=[Depends(get_current_user)])
aggregator = HoldingsAggregator()
logger = get_logger("routes.portfolio")

_STALE_SECONDS = 3600


async def _maybe_sync(source: str | None) -> None:
    """Sync stale sources concurrently; cap at 8 s so the request never hangs."""
    now = datetime.now(UTC)
    targets = [SOURCES[source]] if source else list(SOURCES.values())
    stale = [
        src for src in targets
        if not src._last_synced_at
        or (now - src._last_synced_at).total_seconds() > _STALE_SECONDS
    ]
    if not stale:
        return

    async def _try(src) -> None:
        try:
            await src.sync()
        except Exception:
            logger.warning("Auto-sync failed for %s — returning cached data", src.slug)

    try:
        await asyncio.wait_for(asyncio.gather(*[_try(s) for s in stale]), timeout=8.0)
    except asyncio.TimeoutError:
        logger.warning("Auto-sync timed out after 8 s — returning cached data")


@router.get("/holdings")
async def get_holdings(source: str | None = None):
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
    await _maybe_sync(source)
    return {
        "totals": aggregator.totals(source),
        "allocation": [a.__dict__ for a in aggregator.allocation(source)],
        "holdings": [h.model_dump(mode="json") for h in aggregator.all_holdings(source)],
    }


@router.get("/treemap")
async def get_treemap(source: str | None = None):
    if source and source not in SOURCES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown source: {source}")
    return {
        "totals": aggregator.totals(source),
        "cells": [c.__dict__ for c in aggregator.treemap(source)],
    }


@router.get("/rebalance")
async def get_rebalance():
    drift, suggestions = aggregator.rebalance()
    return {
        "drift": [d.__dict__ for d in drift],
        "suggestions": [s.__dict__ for s in suggestions],
        "targets": {k.value: v for k, v in aggregator.targets.items()},
    }


@router.get("/fx")
async def get_fx():
    """Current FX rates used to roll up cross-currency totals (1-hour CSV cache)."""
    return {
        "inr_per_usd": get_inr_per_usd(),
        "ttl_seconds": _FX_TTL_SECONDS,
    }


@router.get("/wallets")
async def get_wallets():
    return {
        "wallets": [w.model_dump(mode="json") for w in list_wallets()],
    }


@router.post("/wallets/sync")
async def post_sync_wallets():
    refreshed = await sync_all()
    return {
        "wallets": [w.model_dump(mode="json") for w in refreshed.values()],
    }


@router.post("/wallets/{slug}/sync")
async def post_sync_one_wallet(slug: str):
    try:
        info = await sync_one(slug)
    except KeyError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
    except Exception as e:
        logger.exception("Wallet sync failed for %s", slug)
        raise HTTPException(400, f"Wallet sync failed: {e}") from e
    return {"wallet": info.model_dump(mode="json")}


@router.post("/refresh")
async def force_refresh():
    """Hard refresh: bust all CSV caches, re-sync every source + all wallets."""
    for slug in SOURCES:
        clear_csv_cache(slug)

    async def _sync_one(slug: str, src) -> tuple[str, dict]:  # type: ignore[no-untyped-def]
        try:
            h = await src.sync()
            return slug, {"ok": True, "count": len(h)}
        except Exception as e:
            logger.exception("force-refresh: %s failed", slug)
            return slug, {"ok": False, "error": str(e)}

    pairs = await asyncio.gather(*[_sync_one(slug, src) for slug, src in SOURCES.items()])
    wallet_results = await sync_all()
    return {
        "sources": dict(pairs),
        "wallets": [w.model_dump(mode="json") for w in wallet_results.values()],
    }


router.include_router(sources_router, prefix="/sources")
router.include_router(cash_router, prefix="/cash")
