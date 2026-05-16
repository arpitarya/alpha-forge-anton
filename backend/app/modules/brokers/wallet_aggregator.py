"""Per-broker wallet view — free cash + holdings roll-up + sync metadata.

Drives the wallet strip on the Portfolio screen. Wallet cash is fetched
lazily (the home view doesn't need to wait on a CDP round-trip on every
page load); call `sync_one` / `sync_all` to refresh it.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from pydantic import BaseModel

from app.core.logging import get_logger
from app.modules.brokers.base import WalletBalance
from app.modules.brokers.registry import SOURCES

logger = get_logger("brokers.wallets")


class WalletInfo(BaseModel):
    slug: str
    label: str
    supports_cash: bool
    cash: float = 0.0
    currency: str = "INR"
    cash_available: bool = False
    cash_error: str | None = None
    cash_as_of: datetime | None = None
    holdings_value: float = 0.0
    holdings_count: int = 0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    last_synced_at: datetime | None = None


def _aggregate_holdings(slug: str) -> tuple[float, float, float, int]:
    """Return (current_value, invested, pnl, count) across this broker's holdings."""
    src = SOURCES.get(slug)
    if not src:
        return 0.0, 0.0, 0.0, 0
    cv = sum(h.current_value for h in src.cached)
    inv = sum(h.invested for h in src.cached)
    return round(cv, 2), round(inv, 2), round(cv - inv, 2), len(src.cached)


def _build_one(slug: str) -> WalletInfo:
    src = SOURCES[slug]
    bal: WalletBalance | None = src.cash
    if bal is None and getattr(src, "supports_cash", False):
        from app.modules.brokers.cash_dump import read_cached_cash
        bal = read_cached_cash(slug)
        if bal:
            src._cash = bal
    cv, inv, pnl, count = _aggregate_holdings(slug)
    pnl_pct = round((pnl / inv * 100) if inv else 0.0, 2)
    return WalletInfo(
        slug=slug,
        label=src.label,
        supports_cash=bool(getattr(src, "supports_cash", False)),
        cash=bal.cash if bal else 0.0,
        currency=bal.currency if bal else "INR",
        cash_available=bool(bal and bal.available),
        cash_error=bal.error if bal else None,
        cash_as_of=bal.as_of if bal else None,
        holdings_value=cv,
        holdings_count=count,
        pnl=pnl,
        pnl_pct=pnl_pct,
        last_synced_at=src._last_synced_at,
    )


def list_wallets() -> list[WalletInfo]:
    return [_build_one(slug) for slug in SOURCES]


async def sync_one(slug: str) -> WalletInfo:
    src = SOURCES.get(slug)
    if not src or not getattr(src, "supports_cash", False):
        raise KeyError(f"Wallet cash not supported for {slug!r}")
    await src.sync_cash()
    return _build_one(slug)


async def sync_all() -> dict[str, WalletInfo]:
    targets = [s for s in SOURCES.values() if getattr(s, "supports_cash", False)]

    async def _go(s) -> None:  # type: ignore[no-untyped-def]
        try:
            await s.sync_cash()
        except Exception as e:
            logger.warning("wallet sync-all: %s failed: %s", s.slug, e)

    await asyncio.gather(*[_go(s) for s in targets])
    _ = datetime.now(UTC)
    return {slug: _build_one(slug) for slug in SOURCES}
