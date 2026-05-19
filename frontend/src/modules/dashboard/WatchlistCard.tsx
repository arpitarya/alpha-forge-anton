"use client";

import { Card, RiskBars, Text, WatchRow } from "@alphaforge-anton/ravel-ui";
import { useState } from "react";
import {
  useAddWatchlistItem,
  useDashboardRisk,
  useDashboardWatchlist,
  useDeleteWatchlistItem,
} from "@/modules/dashboard";

export function WatchlistCard() {
  const { data: items = [] } = useDashboardWatchlist();
  const { data: risk } = useDashboardRisk();
  const [editing, setEditing] = useState(false);
  const [draftSym, setDraftSym] = useState("");
  const [draftSub, setDraftSub] = useState("");
  const add = useAddWatchlistItem();
  const del = useDeleteWatchlistItem();

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const sym = draftSym.trim();
    if (!sym) return;
    add.mutate(
      { symbol: sym, sublabel: draftSub.trim() },
      {
        onSuccess: () => {
          setDraftSym("");
          setDraftSub("");
        },
      },
    );
  };

  return (
    <Card glow className="flex h-full flex-col gap-4 overflow-hidden">
      <Card.Header
        title="Watchlist"
        right={
          <button
            type="button"
            onClick={() => setEditing((e) => !e)}
            className="rounded border border-[color:var(--line)] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.2em] text-[color:var(--fg-3)] transition hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
          >
            {editing ? "DONE" : "+ EDIT"}
          </button>
        }
      />
      <div className="flex flex-col divide-y divide-dashed divide-[color:var(--line)]">
        {items.map((it) => (
          <div key={it.id ?? it.symbol} className="group relative">
            <WatchRow
              symbol={it.symbol}
              sublabel={it.sublabel}
              price={it.price}
              change={it.change}
              changeTone={it.tone}
              className="!py-2.5"
            />
            {editing && it.id && (
              <button
                type="button"
                onClick={() => del.mutate(it.id as string)}
                title={`Remove ${it.symbol}`}
                aria-label={`Remove ${it.symbol}`}
                className="absolute right-1 top-1/2 -translate-y-1/2 rounded border border-[color:var(--line)] bg-[color:var(--surface)] px-1.5 py-0.5 font-mono text-[10px] text-[color:var(--fg-3)] hover:border-[color:var(--red)] hover:text-[color:var(--red)]"
              >
                ×
              </button>
            )}
          </div>
        ))}
      </div>

      {editing && (
        <form
          onSubmit={submit}
          className="flex flex-col gap-1.5 rounded border border-dashed border-[color:var(--line-hi)] p-2"
        >
          <div className="flex gap-1.5">
            <input
              value={draftSym}
              onChange={(e) => setDraftSym(e.target.value.toUpperCase())}
              placeholder="SYMBOL"
              className="flex-1 rounded border border-[color:var(--line)] bg-transparent px-2 py-1 font-mono text-[11px] uppercase tracking-[0.12em] text-[color:var(--fg)] outline-none focus:border-[color:var(--accent)]"
            />
            <input
              value={draftSub}
              onChange={(e) => setDraftSub(e.target.value)}
              placeholder="NSE · IT"
              className="flex-1 rounded border border-[color:var(--line)] bg-transparent px-2 py-1 font-mono text-[11px] text-[color:var(--fg)] outline-none focus:border-[color:var(--accent)]"
            />
            <button
              type="submit"
              disabled={add.isPending || !draftSym.trim()}
              className="rounded border border-[color:var(--accent)] px-3 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] disabled:opacity-40"
            >
              ADD
            </button>
          </div>
        </form>
      )}

      <hr className="my-2 h-px border-0 bg-[color:var(--line-hi)]" />

      <Card.Header
        title="Risk Meter"
        right={
          <Text variant="tag" tone="accent">
            {risk ? `${risk.confidence.toFixed(1)}%` : "—"}
          </Text>
        }
        className="mb-0"
      />
      {risk && <RiskBars values={risk.bars} activeIndex={risk.active_index} height={56} />}
      {risk && (
        <div className="flex justify-between font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
          <span>Confidence</span>
          <span className="text-[color:var(--accent)]">{risk.confidence.toFixed(1)} / 100</span>
        </div>
      )}
    </Card>
  );
}
