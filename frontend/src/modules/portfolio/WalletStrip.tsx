"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import {
  useForceRefresh,
  useSyncAllSources,
  useSyncAllWallets,
  useWallets,
} from "./portfolio.query";
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
  const syncCash = useSyncAllWallets();
  const syncHoldings = useSyncAllSources();
  const forceRefresh = useForceRefresh();
  const qc = useQueryClient();

  async function handleSyncCash() {
    try {
      await syncCash.mutateAsync();
    } finally {
      qc.invalidateQueries({ queryKey: ["portfolio", "wallets"] });
    }
  }

  async function handleRefreshHoldings() {
    try {
      await syncHoldings.mutateAsync();
    } finally {
      qc.invalidateQueries({ queryKey: ["portfolio", "holdings"] });
      qc.invalidateQueries({ queryKey: ["portfolio", "treemap"] });
      qc.invalidateQueries({ queryKey: ["portfolio", "wallets"] });
    }
  }

  async function handleForceRefresh() {
    try {
      await forceRefresh.mutateAsync();
    } finally {
      qc.invalidateQueries({ queryKey: ["portfolio"] });
    }
  }

  if (isLoading && wallets.length === 0) {
    return (
      <div className="overflow-x-auto pb-1">
        <div className="grid h-[110px] min-w-max grid-cols-[repeat(5,minmax(235px,1fr))] gap-2.5">
          {["all", "zerodha", "angelone", "groww", "wintwealth"].map((k) => (
            <div
              key={k}
              className="animate-pulse rounded-[10px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_60%,transparent)]"
            />
          ))}
        </div>
      </div>
    );
  }

  const cashSynced = wallets.some((w) => w.cash_available);
  const cardColumns = ["minmax(250px, 1.05fr)", ...wallets.map(() => "minmax(235px, 1fr)")].join(
    " ",
  );

  return (
    <div data-component="WalletStrip" className="flex min-w-0 flex-col gap-1.5">
      <div className="flex flex-wrap items-center justify-end gap-2">
        <StripButton
          onClick={handleSyncCash}
          pending={syncCash.isPending}
          label={cashSynced ? "⟳ Refresh cash" : "⟳ Sync cash"}
          pendingLabel="Syncing cash…"
        />
        <StripButton
          onClick={handleRefreshHoldings}
          pending={syncHoldings.isPending}
          label="⟳ Refresh holdings"
          pendingLabel="Refreshing holdings…"
        />
        <StripButton
          onClick={handleForceRefresh}
          pending={forceRefresh.isPending}
          label="⟳ Refresh"
          pendingLabel="Refreshing…"
          dim
        />
      </div>
      <div className="min-w-0 overflow-x-auto pb-1 [scrollbar-gutter:stable]">
        <div className="grid min-w-max gap-2.5" style={{ gridTemplateColumns: cardColumns }}>
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
    </div>
  );
}

function StripButton({
  onClick,
  pending,
  label,
  pendingLabel,
  dim = false,
}: {
  onClick: () => void;
  pending: boolean;
  label: string;
  pendingLabel: string;
  dim?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={pending}
      className={[
        "flex items-center gap-1.5 rounded-[4px] border px-2.5 py-[3px] font-mono text-[9px] uppercase tracking-[0.18em] transition disabled:opacity-40",
        dim
          ? "border-[color:var(--line-hi)] bg-transparent text-[color:var(--fg-3)] hover:border-[color:var(--fg-3)] hover:text-[color:var(--fg)]"
          : "border-[color:color-mix(in_srgb,var(--accent)_35%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_16%,transparent)] hover:shadow-[0_0_10px_var(--glow)]",
      ].join(" ")}
    >
      {pending ? (
        <>
          <span className="inline-block h-1.5 w-1.5 animate-spin rounded-full border border-current border-t-transparent" />
          {pendingLabel}
        </>
      ) : (
        label
      )}
    </button>
  );
}
