"use client";

import { SegmentedControl } from "@alphaforge-anton/ravel-ui";
import { AssetClassFilter } from "./AssetClassFilter";
import { PnLToggle } from "./PnLToggle";
import type { AssetClassCounts, FilterState } from "./portfolio.filter";
import { SearchBox } from "./SearchBox";
import { SortMenu } from "./SortMenu";

export type PortfolioView = "tree" | "ledger";

export interface FilterBarProps {
  filter: FilterState;
  setFilter: (next: Partial<FilterState>) => void;
  counts: AssetClassCounts;
  view: PortfolioView;
  onViewChange: (v: PortfolioView) => void;
}

export function FilterBar({ filter, setFilter, counts, view, onViewChange }: FilterBarProps) {
  return (
    <div data-component="FilterBar" className="relative flex flex-shrink-0 items-center gap-2.5 rounded-[10px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)] px-3 py-2">
      <SearchBox value={filter.query} onChange={(q) => setFilter({ query: q })} />
      <div className="mx-[2px] my-[3px] w-px self-stretch bg-[color:var(--line)]" />
      <AssetClassFilter
        assetClass={filter.assetClass}
        equitySub={filter.equitySub}
        counts={counts}
        onChange={(assetClass, equitySub) => setFilter({ assetClass, equitySub })}
      />
      <div className="mx-[2px] my-[3px] w-px self-stretch bg-[color:var(--line)]" />
      <PnLToggle value={filter.pnl} onChange={(m) => setFilter({ pnl: m })} />
      <SortMenu
        sortBy={filter.sortBy}
        sortDir={filter.sortDir}
        onChange={(sortBy, sortDir) => setFilter({ sortBy, sortDir })}
      />
      <div className="mx-[2px] my-[3px] w-px self-stretch bg-[color:var(--line)]" />
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
