"use client";

import { clsx } from "clsx";
import { useEffect, useRef, useState } from "react";
import { SORT_LABEL, type SortDir, type SortKey } from "./portfolio.filter";

export interface SortMenuProps {
  sortBy: SortKey;
  sortDir: SortDir;
  onChange: (key: SortKey, dir: SortDir) => void;
}

const KEYS: SortKey[] = ["value", "pnl", "pnl_pct", "qty", "alpha"];

export function SortMenu({ sortBy, sortDir, onChange }: SortMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function h(e: MouseEvent) {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [open]);

  function pick(k: SortKey) {
    if (k === sortBy) onChange(k, sortDir === "desc" ? "asc" : "desc");
    else onChange(k, k === "alpha" ? "asc" : "desc");
    setOpen(false);
  }

  return (
    <div ref={ref} className="relative flex-shrink-0">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-2 rounded-[5px] border border-[color:var(--line)] bg-transparent px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-2)] transition hover:border-[color:var(--line-hi)] hover:text-[color:var(--fg)]"
      >
        <span>Sort · {SORT_LABEL[sortBy]}</span>
        <span className="text-[11px] text-[color:var(--accent)]">
          {sortDir === "desc" ? "↓" : "↑"}
        </span>
      </button>
      {open && (
        <div className="absolute right-0 top-[calc(100%+6px)] z-50 flex min-w-[200px] flex-col gap-[2px] rounded-[8px] border border-[color:var(--line-hi)] bg-[color:var(--surface)] p-1.5 shadow-[0_12px_36px_rgba(0,0,0,0.4),0_0_24px_color-mix(in_srgb,var(--accent)_8%,transparent)]">
          {KEYS.map((k) => {
            const active = k === sortBy;
            return (
              <button
                key={k}
                type="button"
                onClick={() => pick(k)}
                className={clsx(
                  "flex items-center justify-between rounded-[4px] px-2.5 py-2 font-mono text-[10px] uppercase tracking-[0.14em] transition",
                  active
                    ? "bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)] text-[color:var(--accent)]"
                    : "text-[color:var(--fg-2)] hover:bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)] hover:text-[color:var(--fg)]",
                )}
              >
                <span>{SORT_LABEL[k]}</span>
                <span
                  className={clsx(
                    "min-w-[10px] text-right text-[11px]",
                    active ? "text-[color:var(--accent)]" : "text-[color:var(--fg-3)]",
                  )}
                >
                  {active ? (sortDir === "desc" ? "↓" : "↑") : ""}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
