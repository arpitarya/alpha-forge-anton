"""System readiness probes used by /health/boot. Each probe returns a
BootService snapshot — never raises, so a single broken probe can't take
the whole boot endpoint down."""

from __future__ import annotations

import time

from sqlalchemy import text

from app.core.database import async_session
from app.modules.brokers.broker_schemas import SourceStatus
from app.modules.brokers.registry import SOURCES
from app.modules.health.boot_schemas import BootService, BootStatus

_LLM_PRIORITY = ["gemini", "cerebras", "groq", "claude-sdk", "mistral", "openrouter", "huggingface"]


async def probe_backend() -> BootService:
    return BootService(
        key="backend",
        label="Backend · FastAPI gateway",
        status=BootStatus.OK,
        detail="online",
    )


async def probe_database() -> BootService:
    started = time.perf_counter()
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        ms = int((time.perf_counter() - started) * 1000)
        return BootService(
            key="database", label="Database · Postgres ready",
            status=BootStatus.OK, detail=f"{ms}ms",
        )
    except Exception as e:  # noqa: BLE001
        return BootService(
            key="database", label="Database · Postgres",
            status=BootStatus.ERROR, detail=str(e)[:48],
        )


async def probe_llm() -> BootService:
    try:
        from alphaforge_anton_llm.gateway import create_gateway
        healths = await create_gateway().health()
        available = {name for name, h in healths.items() if h.available}
        if not available:
            return BootService(
                key="llm", label="AI Gateway · LLM routing",
                status=BootStatus.ERROR, detail="no providers available",
            )
        primary = next((p for p in _LLM_PRIORITY if p in available), next(iter(available)))
        return BootService(
            key="llm", label="AI Gateway · LLM routing",
            status=BootStatus.OK, detail=f"{len(available)} providers · via {primary}",
        )
    except Exception as e:  # noqa: BLE001
        return BootService(
            key="llm", label="AI Gateway · LLM routing",
            status=BootStatus.ERROR, detail=str(e)[:48],
        )


_BROKER_STATUS_MAP = {
    SourceStatus.READY: BootStatus.OK,
    SourceStatus.SYNCING: BootStatus.OK,
    SourceStatus.UNCONFIGURED: BootStatus.WARN,
    SourceStatus.ERROR: BootStatus.ERROR,
}


def _broker_detail(status: SourceStatus, holdings_count: int) -> str:
    if status == SourceStatus.READY:
        return f"{holdings_count} holdings" if holdings_count else "linked · not synced"
    if status == SourceStatus.SYNCING:
        return "syncing…"
    if status == SourceStatus.UNCONFIGURED:
        return "not linked"
    return "error"


async def probe_brokers() -> list[BootService]:
    rows: list[BootService] = []
    for slug, src in SOURCES.items():
        info = src.info()
        rows.append(BootService(
            key=slug,
            label=f"{info.label} · holdings source",
            status=_BROKER_STATUS_MAP.get(info.status, BootStatus.WARN),
            detail=_broker_detail(info.status, info.holdings_count),
        ))
    return rows
