"use client";

import { Ticker } from "@alphaforge-anton/ravel-ui";
import { useState } from "react";
import {
  useAddTickerItem,
  useDashboardTicker,
  useDeleteTickerItem,
} from "@/modules/dashboard";

export function TerminalTicker() {
  const { data: items = [] } = useDashboardTicker();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const add = useAddTickerItem();
  const del = useDeleteTickerItem();

  if (items.length === 0 && !editing) {
    return (
      <div className="flex h-7 items-center gap-2 rounded-[var(--radius-sm)] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)] px-2">
        <button
          type="button"
          onClick={() => setEditing(true)}
          className="ml-auto rounded border border-[color:var(--line)] px-2 font-mono text-[9px] uppercase tracking-[0.2em] text-[color:var(--fg-3)] hover:text-[color:var(--accent)]"
        >
          + Edit
        </button>
      </div>
    );
  }

  return (
    <div className="relative flex items-center gap-2">
      <div className="min-w-0 flex-1">
        <Ticker items={items} speedSeconds={48} />
      </div>
      <button
        type="button"
        onClick={() => setEditing((e) => !e)}
        title={editing ? "Close ticker editor" : "Edit ticker"}
        className="flex-shrink-0 rounded border border-[color:var(--line)] px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.2em] text-[color:var(--fg-3)] transition hover:border-[color:var(--accent)] hover:text-[color:var(--accent)]"
      >
        {editing ? "Done" : "Edit"}
      </button>
      {editing && (
        <div className="absolute left-0 right-0 top-full z-30 mt-1 flex flex-wrap items-center gap-1 rounded border border-[color:var(--line-hi)] bg-[color:var(--surface)] p-2 shadow-lg">
          {items.map((it) => (
            <span
              key={it.id ?? it.symbol}
              className="inline-flex items-center gap-1.5 rounded border border-[color:var(--line)] px-1.5 py-0.5 font-mono text-[10px] text-[color:var(--fg-2)]"
            >
              {it.symbol}
              {it.id && (
                <button
                  type="button"
                  onClick={() => del.mutate(it.id as string)}
                  className="text-[color:var(--fg-3)] hover:text-[color:var(--red)]"
                  aria-label={`Remove ${it.symbol}`}
                  title="Remove"
                >
                  ×
                </button>
              )}
            </span>
          ))}
          <form
            className="flex items-center gap-1"
            onSubmit={(e) => {
              e.preventDefault();
              const sym = draft.trim();
              if (!sym) return;
              add.mutate(sym, { onSuccess: () => setDraft("") });
            }}
          >
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value.toUpperCase())}
              placeholder="ADD SYMBOL"
              className="w-32 rounded border border-[color:var(--line)] bg-transparent px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--fg)] outline-none focus:border-[color:var(--accent)]"
            />
            <button
              type="submit"
              disabled={add.isPending || !draft.trim()}
              className="rounded border border-[color:var(--accent)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] disabled:opacity-40"
            >
              +
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
