"""Health check endpoints."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from app.core.logging import get_logger
from app.modules.brokers.broker_schemas import SourceStatus
from app.modules.brokers.registry import SOURCES
from app.modules.health.boot_probes import (
    probe_backend,
    probe_brokers,
    probe_database,
    probe_llm,
)
from app.modules.health.boot_schemas import BootReport

router = APIRouter()
logger = get_logger("routes.health")


@router.get("/health")
async def health_check():
    logger.debug("Health check hit")
    return {"status": "healthy", "service": "alphaforge-anton-api"}


@router.get("/health/boot", response_model=BootReport)
async def boot_report() -> BootReport:
    """Per-system readiness snapshot consumed by the terminal boot splash.

    Probes return rows in a stable, top-to-bottom order: gateway → database →
    LLM → each connected broker source. Each probe swallows its own errors so
    one failure can't take down the whole report."""
    services = [await probe_backend(), await probe_database(), await probe_llm()]
    services.extend(await probe_brokers())
    return BootReport(services=services)


@router.post("/health/boot/sync")
async def boot_sync():
    """Concurrently sync all non-unconfigured broker sources.

    Called by the boot splash immediately after GET /health/boot. Blocks until
    all syncs settle; the frontend holds navigation until this resolves."""
    results: dict[str, dict] = {}

    async def _sync_one(slug: str) -> None:
        src = SOURCES[slug]
        if src.info().status == SourceStatus.UNCONFIGURED:
            return
        try:
            holdings = await src.sync()
            results[slug] = {"ok": True, "holdings_count": len(holdings), "detail": f"{len(holdings)} holdings"}
        except Exception as e:  # noqa: BLE001
            logger.warning("boot sync failed for %s: %s", slug, e)
            results[slug] = {"ok": False, "holdings_count": 0, "detail": "sync failed"}

    await asyncio.gather(*[_sync_one(slug) for slug in SOURCES])
    return {"results": results}
