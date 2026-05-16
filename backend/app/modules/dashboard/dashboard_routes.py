"""Dashboard read-only feeds for the terminal home screen.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.database import get_db
from app.modules.brokers import HoldingsAggregator
from app.modules.dashboard import dashboard_repo as repo
from app.modules.dashboard.dashboard_schemas import (
    BriefBlock,
    CreateTickerItemRequest,
    CreateWatchlistItemRequest,
    DashboardStats,
    RiskMeter,
    StatCard,
    TerminalBrief,
    TickerItem,
    WatchlistItem,
)
from app.modules.dashboard.dashboard_seed import BRIEF_SEED

router = APIRouter(dependencies=[Depends(get_current_user)])
_agg = HoldingsAggregator()


def _ticker_dto(row) -> TickerItem:
    return TickerItem(
        id=str(row.id), symbol=row.symbol, price=row.price, change=row.change, tone=row.tone,
    )


def _watchlist_dto(row) -> WatchlistItem:
    return WatchlistItem(
        id=str(row.id), symbol=row.symbol, sublabel=row.sublabel,
        price=row.price, change=row.change, tone=row.tone,
    )


@router.get("/ticker", response_model=list[TickerItem])
async def get_ticker(db: AsyncSession = Depends(get_db)):
    return [_ticker_dto(r) for r in await repo.list_ticker(db)]


@router.post("/ticker", response_model=TickerItem, status_code=status.HTTP_201_CREATED)
async def post_ticker(body: CreateTickerItemRequest, db: AsyncSession = Depends(get_db)):
    if not body.symbol.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "symbol required")
    return _ticker_dto(await repo.add_ticker(db, body.symbol))


@router.delete("/ticker/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticker(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await repo.delete_ticker(db, item_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ticker item not found")


@router.get("/watchlist", response_model=list[WatchlistItem])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    return [_watchlist_dto(r) for r in await repo.list_watchlist(db)]


@router.post("/watchlist", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
async def post_watchlist(body: CreateWatchlistItemRequest, db: AsyncSession = Depends(get_db)):
    if not body.symbol.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "symbol required")
    return _watchlist_dto(await repo.add_watchlist(db, body.symbol, body.sublabel))


@router.delete("/watchlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    if not await repo.delete_watchlist(db, item_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "watchlist item not found")


@router.get("/risk", response_model=RiskMeter)
async def get_risk():
    rng = random.Random(int(datetime.now().timestamp()) // 5)
    bars = [
        round(max(20.0, min(95.0, base + rng.uniform(-jit, jit))), 1)
        for base, jit in [(30, 8), (55, 8), (90, 4), (42, 8), (68, 8)]
    ]
    return RiskMeter(bars=bars, active_index=2, confidence=88.4)


@router.get("/brief", response_model=TerminalBrief)
async def get_brief():
    blocks = [BriefBlock(**b) for b in BRIEF_SEED]
    return TerminalBrief(blocks=blocks, generated_at=datetime.now(UTC).isoformat())


def _fmt_inr_short(v: float) -> str:
    a = abs(v)
    if a >= 1_00_00_000:
        return f"₹{v / 1_00_00_000:.2f}Cr"
    if a >= 1_00_000:
        return f"₹{v / 1_00_000:.2f}L"
    return f"₹{int(round(v)):,}"


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    """Net worth = aggregator current_value (INR-normalised); today P&L from broker day_change_pct."""
    t = _agg.totals()
    net = float(t["current_value"])
    day = float(t["day_pnl"])
    day_pct = float(t["day_pnl_pct"])
    up, dn, count = int(t["day_up"]), int(t["day_dn"]), int(t["count"])
    tone = "up" if day >= 0 else "dn"
    arrow = "▲" if day >= 0 else "▼"
    return DashboardStats(
        net_worth=StatCard(
            label="Net Worth", value=net,
            delta=f"{arrow} {day_pct:+.2f}% TODAY · {arrow} {_fmt_inr_short(abs(day))}",
            delta_tone=tone,
            sparkline=None,
        ),
        pnl_today=StatCard(
            label="Today's P&L", value=day,
            delta=f"{count} positions · {up} up / {dn} dn",
            delta_tone=tone,
        ),
        confidence=StatCard(
            label="Confidence", value=88.4, delta="Orb pulse strong", delta_tone="accent",
        ),
    )
