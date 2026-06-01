"""Health check endpoints."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.brokers.broker_schemas import SourceStatus
from app.modules.brokers.registry import SOURCES
from app.modules.health.boot_probes import (
    probe_backend,
    probe_brokers,
    probe_database,
    probe_llm,
    probe_vault,
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
    services = [await probe_backend(), await probe_vault(), await probe_database(), await probe_llm()]
    services.extend(await probe_brokers())
    return BootReport(services=services)


@router.get("/health/boot/sync-stream")
async def boot_sync_stream() -> StreamingResponse:
    """SSE: emits one JSON event per broker as each sync settles.

    Replaces the old blocking POST so the boot splash can patch each row the
    moment its broker resolves instead of waiting for the slowest one."""
    queue: asyncio.Queue[dict] = asyncio.Queue()

    async def _sync_one(slug: str) -> None:
        src = SOURCES[slug]
        if src.info().status == SourceStatus.UNCONFIGURED:
            reason = src.info().error_message or "not linked"
            await queue.put({"slug": slug, "ok": True, "holdings_count": 0,
                             "detail": "not linked", "reason": reason})
            return

        max_attempts = settings.broker_sync_retry_count + 1
        delay = settings.broker_sync_retry_delay_seconds
        last_err: str = "sync failed"

        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(
                    "boot stream: %s retry %d/%d in %ds",
                    slug, attempt, settings.broker_sync_retry_count, delay,
                )
                await asyncio.sleep(delay)
            try:
                holdings = await asyncio.wait_for(src.sync(), timeout=15.0)
                await queue.put({"slug": slug, "ok": True, "holdings_count": len(holdings),
                                 "detail": f"{len(holdings)} holdings"})
                return
            except TimeoutError:
                last_err = "timeout after 15s"
                logger.warning(
                    "boot stream: %s timed out (attempt %d/%d)", slug, attempt + 1, max_attempts,
                )
            except Exception as e:
                last_err = str(e)[:200]
                logger.warning(
                    "boot stream: %s failed (attempt %d/%d) — %s",
                    slug, attempt + 1, max_attempts, e,
                )

        await queue.put({"slug": slug, "ok": False, "holdings_count": 0,
                         "detail": "sync failed", "reason": last_err})

    async def generate():
        tasks = [asyncio.create_task(_sync_one(s)) for s in SOURCES]
        for _ in range(len(SOURCES)):
            yield f"data: {json.dumps(await queue.get())}\n\n"
        await asyncio.gather(*tasks, return_exceptions=True)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
