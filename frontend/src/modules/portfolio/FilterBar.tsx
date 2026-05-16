"use client";

import { SegmentedControl } from "@alphaforge/solar-orb-ui";
import { PnLToggle } from "./PnLToggle";
import type { FilterState } from "./portfolio.filter";
import { SearchBox } from "./SearchBox";
import { SectorChips } from "./SectorChips";
import { SortMenu } from "./SortMenu";

export type PortfolioView = "tree" | "ledger";

export interface FilterBarProps {
  filter: FilterState;
  setFilter: (next: Partial<FilterState>) => void;
  assetClasses: string[];
  counts: Record<string, number>;
  view: PortfolioView;
  onViewChange: (v: PortfolioView) => void;
}

export function FilterBar({
  filter,
  setFilter,
  assetClasses,
  counts,
  view,
  onViewChange,
}: FilterBarProps) {
  return (
    <div className="relative flex flex-shrink-0 items-center gap-2.5 rounded-[10px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)] px-3 py-2">
      <SearchBox value={filter.query} onChange={(q) => setFilter({ query: q })} />
      <div className="mx-[2px] self-stretch w-px bg-[color:var(--line)] my-[3px]" />
      <SectorChips
        sectors={assetClasses}
        value={filter.assetClass}
        counts={counts}
        onChange={(s) => setFilter({ assetClass: s })}
      />
      <div className="mx-[2px] self-stretch w-px bg-[color:var(--line)] my-[3px]" />
      <PnLToggle value={filter.pnl} onChange={(m) => setFilter({ pnl: m })} />
      <SortMenu
        sortBy={filter.sortBy}
        sortDir={filter.sortDir}
        onChange={(sortBy, sortDir) => setFilter({ sortBy, sortDir })}
      />
      <div className="mx-[2px] self-stretch w-px bg-[color:var(--line)] my-[3px]" />
      <SegmentedControl<PortfolioView>
        options={[
          { value: "tree", label: "Tree" },
          { value: "ledger", label: "Ledger" },
        ]}
        value={view}
        onChange={onViewChange}
        className="rounded-[6px]"
      />
    </div>
  );
}
