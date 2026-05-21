"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import { useSyncAllWallets, useWallets } from "./portfolio.query";
import { WalletCard } from "./WalletCard";
import { aggregateSelected } from "./wallet.utils";

export interface WalletStripProps {
  selected: ReadonlySet<string>;
  onToggleSource: (slug: string) => void;
  onSelectAll: () => void;
}

export function WalletStrip({ selected, onToggleSource, onSelectAll }: WalletStripProps) {
  const { data, isLoading } = useWallets();
  const wallets = data?.wallets ?? [];
  const allCard = useMemo(() => aggregateSelected(wallets, selected), [wallets, selected]);
  const allActive = selected.size === 0;
  const syncAll = useSyncAllWallets();
  const qc = useQueryClient();

  async function handleSyncCash() {
    try {
      await syncAll.mutateAsync();
    } finally {
      qc.invalidateQueries({ queryKey: ["portfolio", "wallets"] });
    }
  }

  if (isLoading && wallets.length === 0) {
    return (
      <div className="grid h-[110px] grid-cols-5 gap-2.5">
        {["all", "zerodha", "angelone", "groww", "wintwealth"].map((k) => (
          <div
            key={k}
            className="animate-pulse rounded-[10px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_60%,transparent)]"
          />
        ))}
      </div>
    );
  }

  const cashSynced = wallets.some((w) => w.cash_available);

  return (
    <div data-component="WalletStrip" className="flex flex-col gap-1.5">
      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={handleSyncCash}
          disabled={syncAll.isPending}
          className="flex items-center gap-1.5 rounded-[4px] border border-[color:color-mix(in_srgb,var(--accent)_35%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)] px-2.5 py-[3px] font-mono text-[9px] uppercase tracking-[0.18em] text-[color:var(--accent)] transition hover:bg-[color:color-mix(in_srgb,var(--accent)_16%,transparent)] hover:shadow-[0_0_10px_var(--glow)] disabled:opacity-40"
        >
          {syncAll.isPending ? (
            <>
              <span className="inline-block h-1.5 w-1.5 animate-spin rounded-full border border-[color:var(--accent)] border-t-transparent" />
              Syncing cash…
            </>
          ) : (
            cashSynced ? "⟳ Refresh cash" : "⟳ Sync cash"
          )}
        </button>
      </div>
      <div
        className="grid gap-2.5"
        style={{ gridTemplateColumns: `1.05fr repeat(${wallets.length}, 1fr)` }}
      >
        <WalletCard wallet={allCard} active={allActive} onClick={onSelectAll} />
        {wallets.map((w) => (
          <WalletCard
            key={w.slug}
            wallet={w}
            active={selected.has(w.slug)}
            onClick={() => onToggleSource(w.slug)}
          />
        ))}
      </div>
    </div>
  );
}
