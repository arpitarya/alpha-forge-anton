"""Angel One equity holdings CSV source (smartapi.angelbroking.com export)."""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


class AngelOneCSVSource(BrokerSource):
    slug = "angelone"
    label = "Angel One (CSV)"
    kind = SourceKind.CSV
    notes = "Export via angelone.in → Portfolio → Holdings → Download CSV"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:
        out: list[Holding] = []
        for row in read_csv(stream):
            symbol = pick(row, "Tradingsymbol", "Symbol", "Instrument").upper()
            if not symbol:
                continue
            qty = to_float(pick(row, "Quantity", "Qty"))
            avg = to_float(pick(row, "Average Price", "Avg Price", "Buy Avg"))
            ltp = to_float(pick(row, "LTP", "Last Traded Price", "Current Price"))
            invested = qty * avg
            current_value = to_float(pick(row, "Current Value", "Mkt Value"), qty * ltp)
            pnl = to_float(pick(row, "P&L", "PnL", "Unrealized P&L"), current_value - invested)
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=AssetClass.EQUITY,
                    symbol=symbol,
                    isin=pick(row, "ISIN") or None,
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp or (current_value / qty if qty else 0.0),
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                    exchange=pick(row, "Exchange") or "NSE",
                )
            )
        return out
