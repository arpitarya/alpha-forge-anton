"""SQLAlchemy ORM models for the terminal dashboard feeds.

Single-user app: ticker + watchlist rows are global (no user_id). If multi-user
is added later, add a `user_id` FK + a unique index on `(user_id, sort_order)`.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


class DashboardTickerItem(Base):
    """One symbol that scrolls in the global terminal ticker bar."""

    __tablename__ = "dashboard_ticker_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    # Last-known display values — captured so the strip stays populated even
    # before live prices land. `tone` is "up" or "dn".
    price: Mapped[str] = mapped_column(String(32), nullable=False, default="—")
    change: Mapped[str] = mapped_column(String(16), nullable=False, default="—")
    tone: Mapped[str] = mapped_column(String(4), nullable=False, default="up")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class DashboardWatchlistItem(Base):
    """One row in the terminal-side Watchlist panel."""

    __tablename__ = "dashboard_watchlist_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    sublabel: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    price: Mapped[str] = mapped_column(String(32), nullable=False, default="—")
    change: Mapped[str] = mapped_column(String(16), nullable=False, default="—")
    tone: Mapped[str] = mapped_column(String(4), nullable=False, default="up")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
