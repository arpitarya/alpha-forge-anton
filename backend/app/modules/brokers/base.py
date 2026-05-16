"""BrokerSource ABC + lifecycle (sync, info, reset).

Schemas live in `broker_schemas.py` and are re-exported here for convenience.
"""

from __future__ import annotations

from abc import ABC
from datetime import UTC, datetime

from app.modules.brokers.broker_schemas import (
    AssetClass,
    Holding,
    SourceInfo,
    SourceKind,
    SourceStatus,
    WalletBalance,
)

__all__ = [
    "AssetClass", "BrokerSource", "Holding",
    "SourceInfo", "SourceKind", "SourceStatus", "WalletBalance",
]


class BrokerSource(ABC):
    """Adapter for one holdings provider — override `fetch()`."""

    slug: str
    label: str
    kind: SourceKind

    # When `supports_cash` is True the source overrides `fetch_cash()` and the
    # /portfolio/wallets endpoint will surface a real number; otherwise the
    # wallet card shows "Cash N/A" instead of fabricating zero.
    supports_cash: bool = False

    def __init__(self) -> None:
        self._cached: list[Holding] | None = None
        self._last_synced_at: datetime | None = None
        self._status: SourceStatus = SourceStatus.UNCONFIGURED
        self._error: str | None = None
        self._cash: WalletBalance | None = None
        self.refetch_seconds: int = 0

    async def fetch(self) -> list[Holding]:
        raise NotImplementedError(f"{self.slug}: override fetch()")

    async def fetch_cash(self) -> WalletBalance:
        return WalletBalance(source=self.slug, available=False)

    @property
    def cash(self) -> WalletBalance | None:
        return self._cash

    async def sync_cash(self) -> WalletBalance:
        from app.modules.brokers.cash_dump import cached_sync_cash
        self._cash = await cached_sync_cash(self)
        return self._cash

    async def sync(self) -> list[Holding]:
        self._status = SourceStatus.SYNCING
        try:
            holdings = await self.fetch()
            self._cached = holdings
            self._last_synced_at = datetime.now(UTC)
            self._status = SourceStatus.READY
            self._error = None
            return holdings
        except Exception as e:
            self._status = SourceStatus.ERROR
            self._error = str(e)
            raise

    @property
    def cached(self) -> list[Holding]:
        return self._cached or []

    def info(self) -> SourceInfo:
        return SourceInfo(
            slug=self.slug, label=self.label, kind=self.kind,
            status=self._status, holdings_count=len(self.cached),
            last_synced_at=self._last_synced_at,
            refetch_seconds=self.refetch_seconds,
            error_message=self._error, notes=getattr(self, "notes", None),
        )

    def reset(self) -> None:
        self._cached = None
        self._last_synced_at = None
        self._status = SourceStatus.UNCONFIGURED
        self._error = None
