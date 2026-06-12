"""Background refetch loop — auto-syncs broker sources when their TTL expires.

The loop polls every POLL_INTERVAL seconds and `sync()`s any source older than its
`refetch_seconds` TTL. READY-but-never-synced sources are instead primed once in the
background (at startup, and again when a mid-life vault unlock promotes sources) —
otherwise a broker stays silently empty forever, since the TTL loop skips them.
Failed primes stay empty until a manual POST /portfolio/wallets/{slug}/sync.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from app.core.logging import get_logger
from app.modules.brokers.base import BrokerSource, SourceStatus

logger = get_logger("brokers.refetch")

POLL_INTERVAL = 60  # seconds between staleness checks
_bg_tasks: set[asyncio.Task] = set()  # strong refs so the loop can't GC a running prime


def _is_due(src: BrokerSource) -> bool:
    if src.refetch_seconds <= 0:
        return False
    if src._status in (SourceStatus.UNCONFIGURED, SourceStatus.SYNCING):
        return False
    if src._last_synced_at is None:
        # Never-synced sources are handled by the primer (prime_in_background)
        # — not by this recurring loop, to avoid retrying a broken source
        # every POLL_INTERVAL.
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


def prime_in_background(sources: dict[str, BrokerSource], name: str = "broker-prime") -> None:
    """Fire-and-forget prime of READY, never-synced sources. Called at startup, and
    again by the boot probe when a mid-life vault unlock promotes sources to READY —
    the startup run has passed by then, so without a re-prime they would sit
    'linked · not synced' with zero holdings until a manual sync."""
    task = asyncio.create_task(_prime_unsynced(sources), name=name)
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


async def start_refetch_loop(sources: dict[str, BrokerSource]) -> asyncio.Task:
    # Prime in the background so the app accepts requests immediately,
    # even if some brokers' first sync takes minutes (CDP auth).
    prime_in_background(sources)
    task = asyncio.create_task(_refetch_loop(sources), name="broker-refetch")
    active = [s for s in sources.values() if s.refetch_seconds > 0]
    logger.info(
        "Broker refetch loop started: %d sources, poll_interval=%ds",
        len(active), POLL_INTERVAL,
    )
    return task
