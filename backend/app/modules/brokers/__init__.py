"""Broker source plugins — pluggable adapters for each holdings provider.

Currently only Zerodha (Kite web-login + CSV fallback) is wired in. New
providers slot in by implementing the BrokerSource ABC and registering in
`registry.py`.

Disclaimer: Not SEBI registered investment advice.
"""

from __future__ import annotations

from app.modules.brokers.aggregator import HoldingsAggregator
from app.modules.brokers.base import (
    AssetClass,
    BrokerSource,
    Holding,
    SourceKind,
    SourceStatus,
)
from app.modules.brokers.groww import GrowwCSVSource, GrowwSource
from app.modules.brokers.registry import SOURCES, get_source
from app.modules.brokers.zerodha import ZerodhaCSVSource, ZerodhaKiteSource

__all__ = [
    "SOURCES",
    "AssetClass",
    "BrokerSource",
    "GrowwCSVSource",
    "GrowwSource",
    "Holding",
    "HoldingsAggregator",
    "SourceKind",
    "SourceStatus",
    "ZerodhaCSVSource",
    "ZerodhaKiteSource",
    "get_source",
]
