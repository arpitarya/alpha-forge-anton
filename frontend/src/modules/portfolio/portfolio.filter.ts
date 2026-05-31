import { primaryLabel } from "./ledger.utils";
import type { HoldingDTO } from "./portfolio.types";

export type PnLMode = "all" | "up" | "dn";

/**
 * Top-level asset class bucket shown in the filter chips.
 * Chips are shown only when the bucket has ≥ 1 holding — fully dynamic.
 */
export type AssetClassBucket =
  | "all"
  | "equity"
  | "mfetf"
  | "gold"
  | "crypto"
  | "bond"
  | "cash"
  | "other";

/** Sub-filter applied when {@link FilterState.assetClass} === "equity". */
export type EquitySub = "all" | "in" | "us" | "invitreit";

export const ASSET_BUCKETS: { id: AssetClassBucket; label: string; hasSub?: boolean }[] = [
  { id: "all", label: "All" },
  { id: "equity", label: "Equity", hasSub: true },
  { id: "mfetf", label: "MF/ETF" },
  { id: "gold", label: "Gold" },
  { id: "crypto", label: "Crypto" },
  { id: "bond", label: "Bonds" },
  { id: "cash", label: "Cash" },
  { id: "other", label: "Other" },
];

export const EQUITY_SUBS: { id: EquitySub; label: string }[] = [
  { id: "all", label: "All" },
  { id: "in", label: "India" },
  { id: "us", label: "US" },
  { id: "invitreit", label: "INVIT/REIT" },
];
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
  assetClass: AssetClassBucket;
  equitySub: EquitySub;
  pnl: PnLMode;
  sortBy: SortKey;
  sortDir: SortDir;
}

function isInvitReit(h: HoldingDTO): boolean {
  const sector = (h.sector ?? "").toUpperCase();
  return sector.includes("REIT") || sector.includes("INVIT");
}

function isUSEquity(h: HoldingDTO): boolean {
  if ((h.currency ?? "").toUpperCase() === "USD") return true;
  const ex = (h.exchange ?? "").toUpperCase();
  return ex === "NYSE" || ex === "NASDAQ" || ex === "ARCA" || ex === "AMEX";
}

/** Map a holding to its top-level filter bucket. */
function bucketOf(h: HoldingDTO): AssetClassBucket {
  if (h.asset_class === "equity") return "equity";
  if (h.asset_class === "mutual_fund" || h.asset_class === "etf") return "mfetf";
  if (h.asset_class === "gold") return "gold";
  if (h.asset_class === "crypto") return "crypto";
  if (h.asset_class === "bond") return "bond";
  if (h.asset_class === "cash") return "cash";
  return "other";
}

function equitySubOf(h: HoldingDTO): EquitySub | null {
  if (h.asset_class !== "equity") return null;
  if (isInvitReit(h)) return "invitreit";
  if (isUSEquity(h)) return "us";
  return "in";
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
    if (f.assetClass !== "all") {
      if (bucketOf(h) !== f.assetClass) return false;
      if (f.assetClass === "equity" && f.equitySub !== "all" && equitySubOf(h) !== f.equitySub)
        return false;
    }
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

export interface AssetClassCounts {
  cls: Record<AssetClassBucket, number>;
  sub: Record<EquitySub, number>;
}

export function assetClassCounts(rows: HoldingDTO[]): AssetClassCounts {
  const cls: Record<AssetClassBucket, number> = {
    all: rows.length,
    equity: 0,
    mfetf: 0,
    gold: 0,
    crypto: 0,
    bond: 0,
    cash: 0,
    other: 0,
  };
  const sub: Record<EquitySub, number> = { all: 0, in: 0, us: 0, invitreit: 0 };
  for (const r of rows) {
    const b = bucketOf(r);
    cls[b] += 1;
    if (b === "equity") {
      sub.all += 1;
      const s = equitySubOf(r);
      if (s && s !== "all") sub[s] += 1;
    }
  }
  return { cls, sub };
}
