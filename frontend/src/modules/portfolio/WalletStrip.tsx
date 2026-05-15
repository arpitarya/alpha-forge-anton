"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import { useSyncAllWallets, useWallets } from "./portfolio.query";
import { WalletCard } from "./WalletCard";
import { aggregateAll } from "./wallet.utils";

export interface WalletStripProps {
  source: string;
  onChange: (slug: string) => void;
}

export function WalletStrip({ source, onChange }: WalletStripProps) {
  const { data, isLoading } = useWallets();
  const wallets = data?.wallets ?? [];
  const allCard = useMemo(() => aggregateAll(wallets), [wallets]);
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
    <div className="flex flex-col gap-1.5">
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
        <WalletCard wallet={allCard} active={source === "all"} onClick={() => onChange("all")} />
        {wallets.map((w) => (
          <WalletCard
            key={w.slug}
            wallet={w}
            active={source === w.slug}
            onClick={() => onChange(w.slug)}
          />
        ))}
      </div>
    </div>
  );
}
