"""Background refetch loop — auto-syncs broker sources when their TTL expires.

Each source exposes `refetch_seconds` (read from env at startup). The loop
checks every POLL_INTERVAL seconds and calls `sync()` on any source whose
last_synced_at is older than its TTL. Sources that have never been synced
(last_synced_at is None) are skipped — the first sync must be manual.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.modules.brokers.base import BrokerSource, SourceStatus

logger = get_logger("brokers.refetch")

POLL_INTERVAL = 60  # seconds between staleness checks


def _is_due(src: BrokerSource) -> bool:
    if src.refetch_seconds <= 0:
        return False
    if src._status in (SourceStatus.UNCONFIGURED, SourceStatus.SYNCING):
        return False
    if src._last_synced_at is None:
        return False
    age = (datetime.now(UTC) - src._last_synced_at).total_seconds()
    return age >= src.refetch_seconds


async def _refetch_loop(sources: dict[str, BrokerSource]) -> None:
    while True:
        await asyncio.sleep(POLL_INTERVAL)
        for slug, src in sources.items():
            if not _is_due(src):
                continue
            logger.info("Refetch: auto-syncing %s (TTL=%ds elapsed)", slug, src.refetch_seconds)
            try:
                await src.sync()
                logger.info("Refetch: %s done — %d holdings", slug, len(src.cached))
            except Exception as e:
                logger.warning("Refetch: %s failed — %s", slug, e)


async def start_refetch_loop(sources: dict[str, BrokerSource]) -> asyncio.Task:
    task = asyncio.create_task(_refetch_loop(sources), name="broker-refetch")
    active = [s for s in sources.values() if s.refetch_seconds > 0]
    logger.info(
        "Broker refetch loop started: %d sources, poll_interval=%ds",
        len(active), POLL_INTERVAL,
    )
    return task
