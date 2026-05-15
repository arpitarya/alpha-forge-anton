"use client";

import type { FilterState } from "./portfolio.filter";
import { fmtINRShort } from "./wallet.utils";

export interface SummaryBarProps {
  filter: FilterState;
  source: string;
  sourceLabel: string;
  shownCount: number;
  totalCount: number;
  shownValue: number;
  grandValue: number;
  onReset: () => void;
}

export function SummaryBar({
  filter,
  source,
  sourceLabel,
  shownCount,
  totalCount,
  shownValue,
  grandValue,
  onReset,
}: SummaryBarProps) {
  const pct = grandValue > 0 ? (shownValue / grandValue) * 100 : 0;
  const hasFilter = filter.query.trim() || filter.sector !== "All" || filter.pnl !== "all";
  return (
    <div className="flex flex-shrink-0 items-center gap-3.5 px-1 py-0.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]">
      <span>
        Showing <b className="font-normal text-[color:var(--accent)]">{shownCount}</b> of{" "}
        {totalCount} positions
        {source !== "all" && (
          <>
            {" "}
            · source <b className="font-normal text-[color:var(--accent)]">{sourceLabel}</b>
          </>
        )}
        {filter.sector !== "All" && (
          <>
            {" "}
            · sector <b className="font-normal text-[color:var(--accent)]">{filter.sector}</b>
          </>
        )}
        {filter.pnl === "up" && (
          <>
            {" "}
            · <b className="font-normal text-[color:var(--green)]">Gainers</b>
          </>
        )}
        {filter.pnl === "dn" && (
          <>
            {" "}
            · <b className="font-normal text-[color:var(--red)]">Losers</b>
          </>
        )}
        {filter.query.trim() && (
          <>
            {" "}
            · matching{" "}
            <b className="font-normal text-[color:var(--accent)]">"{filter.query.trim()}"</b>
          </>
        )}
      </span>
      <span className="ml-auto text-[color:var(--fg-2)]">
        {fmtINRShort(shownValue)} <span className="text-[color:var(--fg-4)]">·</span>{" "}
        {pct.toFixed(1)}% of portfolio
      </span>
      {hasFilter && (
        <button
          type="button"
          onClick={onReset}
          className="rounded-[4px] border border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] bg-transparent px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.18em] text-[color:var(--accent)] transition hover:bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)] hover:shadow-[0_0_14px_var(--glow)]"
        >
          Clear filters ×
        </button>
      )}
    </div>
  );
}
