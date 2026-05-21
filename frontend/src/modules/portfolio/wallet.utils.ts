import type { WalletInfoDTO } from "./portfolio.types";

// Brand gradients for the wallet logo chips (kept short — extend as new
// brokers are added). Falls back to a neutral amber.
export const WALLET_BRAND: Record<string, { grad: [string, string]; short: string }> = {
  zerodha: { grad: ["#f17545", "#d24316"], short: "KT" },
  angelone: { grad: ["#3b6eea", "#0a3d8f"], short: "AO" },
  groww: { grad: ["#00d09c", "#00735c"], short: "GW" },
  indmoney: { grad: ["#6366F1", "#3730A3"], short: "IN" },
  tickertape: { grad: ["#F97316", "#C2410C"], short: "TT" },
  all: { grad: ["#FFB454", "#D45A1A"], short: "ALL" },
};

export function walletBrand(slug: string) {
  return (
    WALLET_BRAND[slug] ?? {
      grad: ["#888", "#444"] as [string, string],
      short: slug.slice(0, 2).toUpperCase(),
    }
  );
}

export function fmtINRShort(v: number): string {
  if (!Number.isFinite(v)) return "₹0";
  if (Math.abs(v) >= 1_00_00_000) return `₹${(v / 1_00_00_000).toFixed(2)}Cr`;
  if (Math.abs(v) >= 1_00_000) return `₹${(v / 1_00_000).toFixed(2)}L`;
  return `₹${Math.round(v).toLocaleString("en-IN")}`;
}

export function currencySymbol(code: string | undefined | null): string {
  return code === "USD" ? "$" : "₹";
}

export function fmtMoneyShort(v: number, currency: string | undefined | null): string {
  const sym = currencySymbol(currency);
  if (!Number.isFinite(v)) return `${sym}0`;
  if (currency === "USD") return `${sym}${v.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;
  if (Math.abs(v) >= 1_00_00_000) return `${sym}${(v / 1_00_00_000).toFixed(2)}Cr`;
  if (Math.abs(v) >= 1_00_000) return `${sym}${(v / 1_00_000).toFixed(2)}L`;
  return `${sym}${Math.round(v).toLocaleString("en-IN")}`;
}

export function relTime(iso: string | null): string {
  if (!iso) return "never";
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000);
  if (m < 1) return "now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

/**
 * Static fallback rate, used when the live `/portfolio/fx` query has not yet
 * resolved. Mirrors backend `fx.FALLBACK_INR_PER_USD`.
 */
export const INR_PER_USD = 83.41;

export function toInr(
  value: number,
  currency: string | null | undefined,
  rate: number = INR_PER_USD,
): number {
  if (!currency || currency.toUpperCase() === "INR") return value;
  if (currency.toUpperCase() === "USD") return value * rate;
  return value;
}

/**
 * Aggregate a subset of wallets into a single synthetic "All / Selected" wallet.
 * Pass `slugs` to restrict (used for multi-select); omit to aggregate every wallet.
 */
export function aggregateSelected(
  wallets: WalletInfoDTO[],
  slugs: ReadonlySet<string> | null,
  rate: number = INR_PER_USD,
): WalletInfoDTO {
  const subset = slugs && slugs.size > 0 ? wallets.filter((w) => slugs.has(w.slug)) : wallets;
  const cash = subset.reduce(
    (s, w) => s + (w.cash_available ? toInr(w.cash, w.currency, rate) : 0),
    0,
  );
  const holdings = subset.reduce((s, w) => s + w.holdings_value, 0);
  const count = subset.reduce((s, w) => s + w.holdings_count, 0);
  const pnl = subset.reduce((s, w) => s + w.pnl, 0);
  const inv = holdings - pnl;
  const label =
    slugs && slugs.size > 0 && slugs.size < wallets.length
      ? `${subset.length} selected`
      : "All wallets";
  return {
    slug: "all",
    label,
    supports_cash: true,
    cash,
    currency: "INR",
    cash_available: subset.some((w) => w.cash_available),
    cash_error: null,
    cash_as_of: null,
    holdings_value: holdings,
    holdings_count: count,
    pnl,
    pnl_pct: inv ? (pnl / inv) * 100 : 0,
    last_synced_at: null,
  };
}

export function aggregateAll(
  wallets: WalletInfoDTO[],
  rate: number = INR_PER_USD,
): WalletInfoDTO {
  // Backend returns `holdings_value` / `pnl` already normalised to INR
  // (see brokers/fx.py), so every wallet rolls into the All total. Cash is
  // still reported in its native currency, so convert it here using the
  // live rate from /portfolio/fx (caller passes it in).
  return aggregateSelected(wallets, null, rate);
}
