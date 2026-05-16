"""DB access for terminal ticker + watchlist rows.

On first read, if the table is empty, seeds it from `dashboard_seed.py` so the
terminal isn't blank on a fresh install.
"""

from __future__ import annotations

import uuid
from typing import TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.dashboard_models import (
    DashboardTickerItem,
    DashboardWatchlistItem,
)
from app.modules.dashboard.dashboard_seed import TICKER_SEED, WATCHLIST_SEED

T = TypeVar("T", DashboardTickerItem, DashboardWatchlistItem)


async def _seed_ticker(db: AsyncSession) -> None:
    for i, (sym, price, change, tone) in enumerate(TICKER_SEED):
        db.add(DashboardTickerItem(
            symbol=sym, sort_order=i, price=price, change=change, tone=tone,
        ))
    await db.commit()


async def _seed_watchlist(db: AsyncSession) -> None:
    for i, (sym, sub, price, change, tone) in enumerate(WATCHLIST_SEED):
        db.add(DashboardWatchlistItem(
            symbol=sym, sublabel=sub, sort_order=i,
            price=price, change=change, tone=tone,
        ))
    await db.commit()


async def list_ticker(db: AsyncSession) -> list[DashboardTickerItem]:
    rows = (await db.execute(
        select(DashboardTickerItem).order_by(DashboardTickerItem.sort_order)
    )).scalars().all()
    if not rows:
        await _seed_ticker(db)
        rows = (await db.execute(
            select(DashboardTickerItem).order_by(DashboardTickerItem.sort_order)
        )).scalars().all()
    return list(rows)


async def list_watchlist(db: AsyncSession) -> list[DashboardWatchlistItem]:
    rows = (await db.execute(
        select(DashboardWatchlistItem).order_by(DashboardWatchlistItem.sort_order)
    )).scalars().all()
    if not rows:
        await _seed_watchlist(db)
        rows = (await db.execute(
            select(DashboardWatchlistItem).order_by(DashboardWatchlistItem.sort_order)
        )).scalars().all()
    return list(rows)


async def add_ticker(db: AsyncSession, symbol: str) -> DashboardTickerItem:
    nxt = (await db.execute(
        select(DashboardTickerItem.sort_order)
        .order_by(DashboardTickerItem.sort_order.desc()).limit(1)
    )).scalar() or 0
    item = DashboardTickerItem(symbol=symbol.strip().upper(), sort_order=nxt + 1)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def add_watchlist(
    db: AsyncSession, symbol: str, sublabel: str
) -> DashboardWatchlistItem:
    nxt = (await db.execute(
        select(DashboardWatchlistItem.sort_order)
        .order_by(DashboardWatchlistItem.sort_order.desc()).limit(1)
    )).scalar() or 0
    item = DashboardWatchlistItem(
        symbol=symbol.strip().upper(), sublabel=sublabel.strip(), sort_order=nxt + 1,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_ticker(db: AsyncSession, item_id: uuid.UUID) -> bool:
    res = await db.execute(delete(DashboardTickerItem).where(DashboardTickerItem.id == item_id))
    await db.commit()
    return (res.rowcount or 0) > 0


async def delete_watchlist(db: AsyncSession, item_id: uuid.UUID) -> bool:
    res = await db.execute(
        delete(DashboardWatchlistItem).where(DashboardWatchlistItem.id == item_id)
    )
    await db.commit()
    return (res.rowcount or 0) > 0
