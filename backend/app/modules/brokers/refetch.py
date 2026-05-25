"""Background refetch loop — auto-syncs broker sources when their TTL expires.

Each source exposes `refetch_seconds` (read from env at startup). The loop
checks every POLL_INTERVAL seconds and calls `sync()` on any source whose
last_synced_at is older than its TTL.

On startup, every READY source that has never been synced is primed in the
background (one attempt, fire-and-forget). This avoids the silent-empty bug
where a broker stays invisible in the UI forever because the TTL refetch
intentionally skips never-synced sources. Sources that fail to prime stay
empty until the user manually triggers POST /portfolio/wallets/{slug}/sync.
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
        # Never-synced sources are handled by the one-shot startup primer
        # (_prime_unsynced) — not by this recurring loop, to avoid retrying
        # a broken source every POLL_INTERVAL.
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


async def _prime_one(slug: str, src: BrokerSource) -> None:
    try:
        await src.sync()
        logger.info("Prime: %s synced — %d holdings", slug, len(src.cached))
    except Exception as e:
        logger.warning(
            "Prime: %s failed — %s. "
            "Trigger manually via POST /api/v1/portfolio/wallets/%s/sync.",
            slug, e, slug,
        )


async def _prime_unsynced(sources: dict[str, BrokerSource]) -> None:
    candidates = [
        (slug, src) for slug, src in sources.items()
        if src._status == SourceStatus.READY and src._last_synced_at is None
    ]
    if not candidates:
        return
    logger.info("Prime: syncing %d never-synced source(s): %s",
                len(candidates), [s for s, _ in candidates])
    await asyncio.gather(
        *(_prime_one(s, src) for s, src in candidates),
        return_exceptions=True,
    )


async def start_refetch_loop(sources: dict[str, BrokerSource]) -> asyncio.Task:
    # Fire-and-forget the startup primer so the app can accept requests
    # immediately, even if some brokers' first sync takes minutes (CDP auth).
    asyncio.create_task(_prime_unsynced(sources), name="broker-prime")
    task = asyncio.create_task(_refetch_loop(sources), name="broker-refetch")
    active = [s for s in sources.values() if s.refetch_seconds > 0]
    logger.info(
        "Broker refetch loop started: %d sources, poll_interval=%ds",
        len(active), POLL_INTERVAL,
    )
    return task
