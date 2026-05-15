"""Wint Wealth holdings CSV source (wintwealth.com → Portfolio → Export).

Wint Wealth CSV columns (bonds/NCDs):
  Security Name, ISIN, Units, Purchase Price, Current Price, Invested, Current Value, P&L
Wint Wealth CSV columns (SGBs):
  Security Name, ISIN, Units, Purchase Price, Current Price, Invested, Current Value, P&L, Asset Type
"""

from __future__ import annotations

from typing import IO

from app.modules.brokers._csv_helper import pick, read_csv, to_float
from app.modules.brokers.base import AssetClass, BrokerSource, Holding, SourceKind


class WintWealthCSVSource(BrokerSource):
    slug = "wintwealth"
    label = "Wint Wealth (CSV)"
    kind = SourceKind.CSV
    notes = "Export via wintwealth.com → Portfolio → Download CSV"

    def parse(self, stream: IO[bytes], filename: str | None = None) -> list[Holding]:  # noqa: ARG002
        out: list[Holding] = []
        for row in read_csv(stream):
            symbol = pick(row, "ISIN", "Security Name", "Instrument Name", "Bond Name").upper()
            if not symbol:
                continue
            isin = pick(row, "ISIN") or None
            name = pick(row, "Security Name", "Instrument Name", "Bond Name") or None
            atype = pick(row, "Asset Type", "Type", "Category").upper()
            asset_class = AssetClass.GOLD if any(k in atype for k in ("SGB", "GOLD")) else AssetClass.BOND
            qty = to_float(pick(row, "Units", "Quantity", "Qty"))
            avg = to_float(pick(row, "Purchase Price", "Avg Buy Price", "Average Price", "Face Value"))
            ltp = to_float(pick(row, "Current Price", "Current NAV", "LTP"))
            invested = to_float(pick(row, "Invested", "Invested Amount", "Purchase Value"), qty * avg)
            current_value = to_float(pick(row, "Current Value", "Current Amount"), qty * ltp)
            pnl = to_float(pick(row, "P&L", "Returns", "Gain/Loss"), current_value - invested)
            out.append(
                Holding(
                    source=self.slug, asset_class=asset_class,
                    symbol=symbol, name=name, isin=isin,
                    quantity=qty, avg_price=avg,
                    last_price=ltp or (current_value / qty if qty else 0.0),
                    invested=invested, current_value=current_value, pnl=pnl,
                    pnl_pct=(pnl / invested * 100) if invested else 0.0,
                    exchange=pick(row, "Exchange") or None,
                )
            )
        return out
