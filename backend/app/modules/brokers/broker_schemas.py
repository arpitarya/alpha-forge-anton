"""Broker domain enums + Pydantic schemas (Holding, SourceInfo)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITY = "equity"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    BOND = "bond"
    GOLD = "gold"
    CRYPTO = "crypto"
    CASH = "cash"
    OTHER = "other"


class SourceKind(str, Enum):
    API = "api"


class SourceStatus(str, Enum):
    UNCONFIGURED = "unconfigured"
    READY = "ready"
    SYNCING = "syncing"
    ERROR = "error"


class Holding(BaseModel):
    source: str
    asset_class: AssetClass
    symbol: str
    name: str | None = None
    isin: str | None = None
    quantity: float
    avg_price: float
    last_price: float
    invested: float
    current_value: float
    pnl: float
    pnl_pct: float
    # Today's percentage move (close-vs-prev-close). 0 when the broker doesn't
    # expose it — aggregator's today-P&L just skips those holdings.
    day_change_pct: float = 0.0
    currency: str = "INR"
    sector: str | None = None
    exchange: str | None = None
    as_of: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SourceInfo(BaseModel):
    slug: str
    label: str
    kind: SourceKind
    status: SourceStatus
    holdings_count: int = 0
    last_synced_at: datetime | None = None
    refetch_seconds: int = 0
    error_message: str | None = None
    notes: str | None = None


class WalletBalance(BaseModel):
    """Free cash sitting inside a broker wallet (not deployed in holdings)."""
    source: str
    currency: str = "INR"
    cash: float = 0.0
    # When the cash figure was last refreshed by the broker (None if never fetched).
    as_of: datetime | None = None
    # `available` is True when the broker exposes a cash endpoint we can read.
    available: bool = True
    error: str | None = None
