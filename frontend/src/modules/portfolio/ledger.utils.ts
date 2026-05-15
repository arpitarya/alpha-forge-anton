import type { HoldingDTO } from "./portfolio.types";

const NAMED_CLASSES = new Set(["bond", "gold"]);

/** Returns the primary visible label for the Symbol column — matches LedgerRow display logic. */
export function primaryLabel(h: HoldingDTO): string {
  return NAMED_CLASSES.has(h.asset_class) && h.name ? h.name : h.symbol;
}

export const ASSET_LABEL: Record<string, string> = {
  equity: "Equity",
  mutual_fund: "MF",
  etf: "ETF",
  bond: "Bond",
  gold: "Gold",
  crypto: "Crypto",
  cash: "Cash",
  other: "Other",
};

export const LEDGER_HEADERS = ["Symbol", "Source", "Class", "Qty", "Avg", "LTP", "Value", "P&L"];
