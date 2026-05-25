"""Process-wide registry of broker sources.

Holds one BrokerSource instance per slug. State (cached holdings + last
sync timestamp) is in-memory; persistence to disk/DB is a layer above.
"""

from __future__ import annotations

from app.modules.brokers.angelone import AngelOneSource
from app.modules.brokers.base import BrokerSource
from app.modules.brokers.binance import BinanceSource
from app.modules.brokers.groww import GrowwSource
from app.modules.brokers.indmoney import IndMoneySource
from app.modules.brokers.tickertape import TickerTapeSource
from app.modules.brokers.zerodha_kite import ZerodhaKiteSource
from app.modules.brokers.zerodha_coin import ZerodhaCoinSource


def _build_sources() -> dict[str, BrokerSource]:
    instances: list[BrokerSource] = [
        ZerodhaKiteSource(),   # slug: zerodha
        GrowwSource(),         # slug: groww      (CDP browser fetch)
        AngelOneSource(),      # slug: angelone   (CDP browser fetch)
        IndMoneySource(),      # slug: indmoney   (CDP browser fetch)
        TickerTapeSource(),    # slug: tickertape (CDP browser fetch; gold)
        BinanceSource(),       # slug: binance      (CDP browser fetch; crypto, USD)
        ZerodhaCoinSource(),   # slug: zerodha_coin (Kite enctoken; MF via Coin)
    ]
    return {s.slug: s for s in instances}


SOURCES: dict[str, BrokerSource] = _build_sources()


def get_source(slug: str) -> BrokerSource:
    src = SOURCES.get(slug)
    if not src:
        raise KeyError(f"Unknown broker source: {slug!r}")
    return src
