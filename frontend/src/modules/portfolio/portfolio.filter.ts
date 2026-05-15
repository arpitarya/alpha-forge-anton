import { primaryLabel } from "./ledger.utils";
import type { HoldingDTO } from "./portfolio.types";

export type PnLMode = "all" | "up" | "dn";
export type SortKey =
  | "value"
  | "pnl"
  | "pnl_pct"
  | "qty"
  | "alpha"
  | "source"
  | "asset_class"
  | "avg_price"
  | "last_price";
export type SortDir = "asc" | "desc";

export interface FilterState {
  query: string;
  sector: string;
  pnl: PnLMode;
  sortBy: SortKey;
  sortDir: SortDir;
}

export const SORT_LABEL: Record<SortKey, string> = {
  value: "Value",
  pnl: "P&L",
  pnl_pct: "P&L %",
  qty: "Quantity",
  alpha: "A → Z",
  source: "Source",
  asset_class: "Class",
  avg_price: "Avg",
  last_price: "LTP",
};

const KEY: Record<SortKey, (h: HoldingDTO) => number | string> = {
  value: (h) => h.current_value,
  pnl: (h) => h.pnl,
  pnl_pct: (h) => h.pnl_pct,
  qty: (h) => h.quantity,
  alpha: (h) => primaryLabel(h),
  source: (h) => h.source,
  asset_class: (h) => h.asset_class,
  avg_price: (h) => h.avg_price,
  last_price: (h) => h.last_price,
};

function matchQuery(h: HoldingDTO, q: string): boolean {
  if (!q) return true;
  const s = q.toLowerCase();
  return [h.symbol, h.name, h.sector, h.exchange, h.source].some((v) =>
    (v ?? "").toLowerCase().includes(s),
  );
}

export function applyFilter(rows: HoldingDTO[], f: FilterState): HoldingDTO[] {
  const filtered = rows.filter((h) => {
    if (f.sector !== "All" && (h.sector ?? "Other") !== f.sector) return false;
    if (f.pnl === "up" && h.pnl <= 0) return false;
    if (f.pnl === "dn" && h.pnl >= 0) return false;
    return matchQuery(h, f.query.trim());
  });
  const dir = f.sortDir === "asc" ? 1 : -1;
  const getter = KEY[f.sortBy];
  return [...filtered].sort((a, b) => {
    const va = getter(a);
    const vb = getter(b);
    if (typeof va === "string" && typeof vb === "string")
      return va.localeCompare(vb, "en", { numeric: true, sensitivity: "base" }) * dir;
    return ((va as number) - (vb as number)) * dir;
  });
}

export function sectorCounts(rows: HoldingDTO[]): Record<string, number> {
  const out: Record<string, number> = { All: rows.length };
  for (const r of rows) {
    const k = r.sector ?? "Other";
    out[k] = (out[k] ?? 0) + 1;
  }
  return out;
}
