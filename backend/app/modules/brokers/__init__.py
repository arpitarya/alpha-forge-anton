"""Broker source plugins — pluggable CDP/API adapters for each holdings provider."""

from __future__ import annotations

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.registry import SOURCES, get_source
from app.modules.brokers.zerodha import ZerodhaKiteSource

__all__ = [
    "SOURCES",
    "AssetClass",
    "BrokerSource",
    "Holding",
    "HoldingsAggregator",
    "SourceKind",
    "SourceStatus",
    "ZerodhaKiteSource",
    "get_source",
]
