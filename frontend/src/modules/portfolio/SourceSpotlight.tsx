"use client";

import { useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { useSyncWallet } from "./portfolio.query";
import type { WalletInfoDTO } from "./portfolio.types";
import { fmtMoneyShort, relTime, walletBrand } from "./wallet.utils";

export interface SourceSpotlightProps {
  wallet: WalletInfoDTO;
  onClear: () => void;
}

export function SourceSpotlight({ wallet, onClear }: SourceSpotlightProps) {
  const brand = walletBrand(wallet.slug);
  const pnlCls = wallet.pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  const sync = useSyncWallet();
  const qc = useQueryClient();

  async function onRefresh() {
    try {
      await sync.mutateAsync(wallet.slug);
    } finally {
      qc.invalidateQueries({ queryKey: ["portfolio", "wallets"] });
    }
  }

  return (
    <div data-component="SourceSpotlight" data-broker={wallet.slug} className="relative flex items-center gap-4 overflow-hidden rounded-[10px] border border-[color:color-mix(in_srgb,var(--accent)_40%,var(--line))] bg-[color:color-mix(in_srgb,var(--surface)_92%,transparent)] px-3.5 py-2.5 shadow-[inset_0_0_32px_color-mix(in_srgb,var(--accent)_6%,transparent)]">
      <span className="pointer-events-none absolute left-0 top-0 bottom-0 w-[3px] bg-[color:var(--accent)] shadow-[0_0_12px_var(--glow)]" />
      <div
        className="grid h-[42px] w-[42px] flex-shrink-0 place-items-center rounded-[9px] font-mono text-[13px] font-bold tracking-[0.04em] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.2),inset_0_-6px_12px_rgba(0,0,0,0.2)]"
        style={{ background: `linear-gradient(135deg, ${brand.grad[0]}, ${brand.grad[1]})` }}
      >
        {brand.short}
      </div>
      <div className="flex-shrink-0">
        <div className="text-[15px] font-medium tracking-[-0.005em]">{wallet.label}</div>
        <div className="mt-[3px] font-mono text-[9.5px] uppercase tracking-[0.16em] text-[color:var(--fg-3)]">
          last sync {relTime(wallet.last_synced_at)} ago
        </div>
      </div>
      <SpotStat label="POSITIONS" value={wallet.holdings_count.toString()} />
      <SpotStat label="HOLDINGS" value={fmtMoneyShort(wallet.holdings_value, wallet.currency)} />
      <SpotStat
        label="P&L"
        value={`${wallet.pnl >= 0 ? "+" : "−"}${fmtMoneyShort(Math.abs(wallet.pnl), wallet.currency)} (${wallet.pnl >= 0 ? "+" : ""}${wallet.pnl_pct.toFixed(2)}%)`}
        valueClass={pnlCls}
      />
      <SpotStat label="CASH" value={wallet.cash_available ? fmtMoneyShort(wallet.cash, wallet.currency) : "—"} />
      <div className="ml-auto flex flex-shrink-0 gap-2">
        <button
          type="button"
          onClick={onRefresh}
          disabled={sync.isPending}
          className="rounded-[5px] border border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--accent)] transition hover:bg-[color:color-mix(in_srgb,var(--accent)_18%,transparent)] hover:shadow-[0_0_14px_var(--glow)] disabled:opacity-50"
        >
          {sync.isPending ? "Refreshing…" : "⟳ Refresh"}
        </button>
        <button
          type="button"
          onClick={onClear}
          className="rounded-[5px] border border-[color:var(--line-hi)] bg-transparent px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--fg-3)] transition hover:border-[color:var(--fg-3)] hover:bg-[color:color-mix(in_srgb,var(--fg-3)_10%,transparent)] hover:text-[color:var(--fg)]"
        >
          Show all ×
        </button>
      </div>
    </div>
  );
}

function SpotStat({
  label,
  value,
  valueClass,
}: {
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div className="flex min-w-[88px] flex-col gap-[2px]">
      <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
        {label}
      </span>
      <span
        className={clsx("text-[14px] font-medium tabular-nums tracking-[-0.005em]", valueClass)}
      >
        {value}
      </span>
    </div>
  );
}
