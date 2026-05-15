"use client";

import { clsx } from "clsx";
import type { WalletInfoDTO } from "./portfolio.types";
import { fmtINRShort, relTime, walletBrand } from "./wallet.utils";

export interface WalletCardProps {
  wallet: WalletInfoDTO;
  active: boolean;
  onClick: () => void;
}

export function WalletCard({ wallet, active, onClick }: WalletCardProps) {
  const brand = walletBrand(wallet.slug);
  const pnlCls = wallet.pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  const cashTxt = wallet.cash_available
    ? fmtINRShort(wallet.cash)
    : wallet.supports_cash
      ? "—"
      : "N/A";
  const sub =
    wallet.slug === "all" ? `${wallet.holdings_count} POSITIONS` : wallet.label.toUpperCase();
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "relative flex flex-col gap-2 overflow-hidden rounded-[10px] border p-3 text-left transition",
        "bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)]",
        active
          ? "border-[color:color-mix(in_srgb,var(--accent)_70%,transparent)] shadow-[inset_0_0_28px_color-mix(in_srgb,var(--accent)_10%,transparent),0_0_28px_var(--glow)]"
          : "border-[color:var(--line)] hover:border-[color:var(--line-hi)] hover:-translate-y-[1px]",
      )}
    >
      {active && (
        <span className="pointer-events-none absolute left-0 top-0 bottom-0 w-[3px] bg-[color:var(--accent)] shadow-[0_0_12px_var(--glow)]" />
      )}
      <div className="flex items-center gap-2.5">
        <div
          className="grid h-[34px] w-[34px] flex-shrink-0 place-items-center rounded-[8px] font-mono text-[11px] font-bold tracking-[0.04em] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.18),inset_0_-4px_8px_rgba(0,0,0,0.18)]"
          style={{ background: `linear-gradient(135deg, ${brand.grad[0]}, ${brand.grad[1]})` }}
        >
          {brand.short}
        </div>
        <div className="flex min-w-0 flex-1 flex-col leading-tight">
          <span className="truncate text-[13px] font-medium text-[color:var(--fg)]">
            {wallet.label}
          </span>
          <span className="mt-[3px] truncate font-mono text-[9px] uppercase tracking-[0.16em] text-[color:var(--fg-3)]">
            {sub}
          </span>
        </div>
        <span className="inline-flex flex-shrink-0 items-center gap-1.5 font-mono text-[9px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[color:var(--green)] shadow-[0_0_6px_var(--green)]" />
          {relTime(wallet.last_synced_at)}
        </span>
      </div>
      <div className="flex items-baseline justify-between gap-2">
        <div>
          <div
            className={clsx(
              "text-[22px] font-medium leading-[1.05] tabular-nums",
              active ? "text-[color:var(--accent)]" : "text-[color:var(--fg)]",
            )}
          >
            {cashTxt}
          </div>
          <div className="mt-[2px] font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
            {wallet.slug === "all" ? "TOTAL CASH" : "FREE CASH"}
          </div>
        </div>
      </div>
      <div className="mt-0.5 flex items-center justify-between border-t border-[color:var(--line)] pt-2 font-mono text-[10px] uppercase tracking-[0.1em] text-[color:var(--fg-3)] tabular-nums">
        <span>
          <span className="font-medium text-[color:var(--fg)]">
            {fmtINRShort(wallet.holdings_value)}
          </span>
          <span className="text-[color:var(--fg-3)]"> · {wallet.holdings_count} POS</span>
        </span>
        <span className={pnlCls}>
          {wallet.pnl >= 0 ? "+" : ""}
          {wallet.pnl_pct.toFixed(2)}%
        </span>
      </div>
    </button>
  );
}
