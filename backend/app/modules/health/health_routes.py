"""Health check endpoints."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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
            # Pull the actual unconfigured-reason if the source recorded one
            # (e.g. "vault is locked, cannot load: ZERODHA_USER_ID") so the UI
            # can suggest the right fix instead of generic "not linked".
            reason = src.info().error_message or "not linked"
            await queue.put({"slug": slug, "ok": True, "holdings_count": 0,
                             "detail": "not linked", "reason": reason})
            return
        try:
            holdings = await asyncio.wait_for(src.sync(), timeout=15.0)
            await queue.put({"slug": slug, "ok": True, "holdings_count": len(holdings),
                             "detail": f"{len(holdings)} holdings"})
        except asyncio.TimeoutError:
            logger.warning("boot stream: %s timed out after 15s", slug)
            await queue.put({"slug": slug, "ok": False, "holdings_count": 0,
                             "detail": "sync failed", "reason": "timeout after 15s"})
        except Exception as e:  # noqa: BLE001
            logger.warning("boot stream: %s failed — %s", slug, e)
            await queue.put({"slug": slug, "ok": False, "holdings_count": 0,
                             "detail": "sync failed", "reason": str(e)[:200]})

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
