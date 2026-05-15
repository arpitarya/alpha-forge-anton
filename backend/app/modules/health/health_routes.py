"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.logging import get_logger
from app.modules.health.boot_probes import (
    probe_backend,
    probe_brokers,
    probe_database,
)
from app.modules.health.boot_schemas import BootReport

router = APIRouter()
logger = get_logger("routes.health")


@router.get("/health")
async def health_check():
    logger.debug("Health check hit")
    return {"status": "healthy", "service": "alphaforge-api"}


@router.get("/health/boot", response_model=BootReport)
async def boot_report() -> BootReport:
    """Per-system readiness snapshot consumed by the terminal boot splash.

    Probes return rows in a stable, top-to-bottom order: gateway → database →
    each connected broker source. Each probe swallows its own errors so one
    failure can't take down the whole report."""
    services = [await probe_backend(), await probe_database()]
    services.extend(await probe_brokers())
    return BootReport(services=services)
