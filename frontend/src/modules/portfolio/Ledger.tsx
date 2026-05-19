"use client";

import { Card, Text } from "@alphaforge-anton/ravel-ui";
import { clsx } from "clsx";
import { LedgerRow } from "./LedgerRow";
import type { SortDir, SortKey } from "./portfolio.filter";
import type { HoldingDTO } from "./portfolio.types";

interface ColDef {
  label: string;
  align: "left" | "right";
  sort?: SortKey;
}

const COLS: ColDef[] = [
  { label: "Symbol", align: "left", sort: "alpha" },
  { label: "Source", align: "right", sort: "source" },
  { label: "Class", align: "right", sort: "asset_class" },
  { label: "Qty", align: "right", sort: "qty" },
  { label: "Avg", align: "right", sort: "avg_price" },
  { label: "LTP", align: "right", sort: "last_price" },
  { label: "Value", align: "right", sort: "value" },
  { label: "P&L", align: "right", sort: "pnl" },
];

export interface LedgerProps {
  holdings: HoldingDTO[];
  query?: string;
  sortBy: SortKey;
  sortDir: SortDir;
  onSort: (key: SortKey, dir: SortDir) => void;
}

export function Ledger({ holdings, query, sortBy, sortDir, onSort }: LedgerProps) {
  return (
    <Card className="h-full overflow-hidden !p-0">
      <div className="h-full overflow-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead className="sticky top-0 z-10 bg-[color:var(--surface)]">
            <tr>
              {COLS.map((c) => {
                const active = c.sort === sortBy;
                const sortable = !!c.sort;
                return (
                  <th
                    key={c.label}
                    onClick={() => {
                      if (!c.sort) return;
                      if (active) onSort(c.sort, sortDir === "desc" ? "asc" : "desc");
                      else {
                        const isText =
                          c.sort === "alpha" || c.sort === "source" || c.sort === "asset_class";
                        onSort(c.sort, isText ? "asc" : "desc");
                      }
                    }}
                    className={clsx(
                      "border-b border-[color:var(--line-hi)] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)] first:pl-6 last:pr-6",
                      c.align === "right" ? "text-right" : "text-left",
                      sortable && "cursor-pointer transition-colors hover:text-[color:var(--fg)]",
                      active && "text-[color:var(--accent)]",
                    )}
                  >
                    <span>{c.label}</span>
                    {sortable && (
                      <span
                        className={clsx(
                          "ml-1.5 text-[10px]",
                          active ? "text-[color:var(--accent)]" : "text-[color:var(--fg-4)]",
                        )}
                      >
                        {active ? (sortDir === "desc" ? "↓" : "↑") : "·"}
                      </span>
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => (
              <LedgerRow key={`${h.source}-${h.symbol}-${h.isin ?? ""}`} h={h} query={query} />
            ))}
          </tbody>
        </table>
        {holdings.length === 0 && (
          <div className="p-12 text-center">
            <Text variant="body-sm" tone="subtle">
              No positions match these filters.
            </Text>
          </div>
        )}
      </div>
    </Card>
  );
}
