"""Groww equity/MF holdings CSV source (groww.in → Portfolio → Export).

Groww CSV columns (equity):  Symbol, ISIN, Exchange, Quantity, Average Price, LTP, Invested, Current Value, P&L
Groww CSV columns (MF):      Fund Name, ISIN, Units, NAV, Invested, Current Value, P&L
"""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


class GrowwCSVSource(BrokerSource):
    slug = "groww"
    label = "Groww (CSV)"
    kind = SourceKind.CSV
    notes = "Export via groww.in → Portfolio → Stocks / Mutual Funds → Download"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in read_csv(stream):
            symbol = pick(row, "Symbol", "Fund Name", "Instrument").upper()
            if not symbol:
                continue
            isin = pick(row, "ISIN") or None
            is_mf = bool(pick(row, "Units") or pick(row, "NAV"))
            asset_class = AssetClass.MF if is_mf else AssetClass.EQUITY
            qty = to_float(pick(row, "Quantity", "Units", "Qty"))
            avg = to_float(pick(row, "Average Price", "Avg Price", "NAV"))
            ltp = to_float(pick(row, "LTP", "Current NAV", "Current Price"))
            invested = to_float(pick(row, "Invested"), qty * avg)
            current_value = to_float(pick(row, "Current Value"), qty * ltp)
            pnl = to_float(pick(row, "P&L", "PnL"), current_value - invested)
            out.append(
                Holding(
                    source=self.slug,
                    asset_class=asset_class,
                    symbol=symbol,
                    isin=isin,
                    quantity=qty,
                    avg_price=avg,
                    last_price=ltp or (current_value / qty if qty else 0.0),
                    invested=invested,
                    current_value=current_value,
                    pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                    exchange=pick(row, "Exchange") or ("NSE" if not is_mf else None),
                )
            )
        return out
