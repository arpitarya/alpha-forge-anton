"use client";

import { AppShell } from "@alphaforge-anton/ravel-ui";
import { useEffect, useMemo, useState } from "react";
import { TerminalTicker, TerminalTopBar } from "@/modules/dashboard";
import type { FilterState } from "@/modules/portfolio";
import {
  applyFilter,
  assetClassCounts,
  FilterBar,
  Ledger,
  PortfolioCompactBar,
  type PortfolioView,
  RebalanceRail,
  SourceSpotlight,
  SummaryBar,
  Treemap,
  useFx,
  useHoldings,
  useWallets,
  WalletStrip,
} from "@/modules/portfolio";
import { aggregateSelected, INR_PER_USD, toInr } from "@/modules/portfolio/wallet.utils";

const DEFAULT_FILTER: FilterState = {
  query: "",
  assetClass: "all",
  equitySub: "all",
  pnl: "all",
  // Default to name (A→Z) so the ledger reads alphabetically on first load.
  sortBy: "alpha",
  sortDir: "asc",
};

export default function PortfolioPage() {
  const [view, setView] = useState<PortfolioView>("ledger");
  // Empty set === "All wallets". Otherwise the set holds the selected broker slugs.
  const [selected, setSelected] = useState<ReadonlySet<string>>(() => new Set());
  const [expanded, setExpanded] = useState<boolean>(false);
  const [railCollapsed, setRailCollapsed] = useState<boolean>(false);
  useEffect(() => {
    try {
      setRailCollapsed(localStorage.getItem("pf-rail-collapsed") === "1");
    } catch {
      /* localStorage unavailable */
    }
  }, []);
  const toggleRail = () => {
    setRailCollapsed((c) => {
      const next = !c;
      try {
        localStorage.setItem("pf-rail-collapsed", next ? "1" : "0");
      } catch {
        /* ignore */
      }
      return next;
    });
  };
  const [filter, setFilterState] = useState<FilterState>(DEFAULT_FILTER);
  const setFilter = (patch: Partial<FilterState>) => setFilterState((f) => ({ ...f, ...patch }));

  const toggleSource = (slug: string) =>
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(slug)) next.delete(slug);
      else next.add(slug);
      return next;
    });
  const selectAll = () => setSelected(new Set());

  // Always fetch the full holdings list — multi-select filtering happens client-side
  // so totals/aggregations stay coherent with the wallet pills.
  const { data: holdingsData } = useHoldings();
  const { data: walletsData } = useWallets();
  const { data: fxData } = useFx();
  const fxRate = fxData?.inr_per_usd ?? INR_PER_USD;
  const allHoldings = holdingsData?.holdings ?? [];

  const sourceFiltered = useMemo(
    () => (selected.size === 0 ? allHoldings : allHoldings.filter((h) => selected.has(h.source))),
    [allHoldings, selected],
  );

  // Asset class counts respect search + pnl (so chips show what's left).
  const counts = useMemo(() => {
    const base = applyFilter(sourceFiltered, { ...filter, assetClass: "all", equitySub: "all" });
    return assetClassCounts(base);
  }, [sourceFiltered, filter]);

  const filtered = useMemo(() => applyFilter(sourceFiltered, filter), [sourceFiltered, filter]);
  // USD holdings (IndMoney US) must be converted to INR before summing — see
  // backend brokers/fx.py for the matching rate constant.
  const shownValue = useMemo(
    () => filtered.reduce((s, h) => s + toInr(h.current_value, h.currency, fxRate), 0),
    [filtered, fxRate],
  );
  const grandValue = useMemo(
    () => allHoldings.reduce((s, h) => s + toInr(h.current_value, h.currency, fxRate), 0),
    [allHoldings, fxRate],
  );

  const wallets = walletsData?.wallets ?? [];
  // SourceSpotlight only makes sense when exactly one broker is selected.
  const singleSelectedWallet = useMemo(() => {
    if (selected.size !== 1) return null;
    const [slug] = [...selected];
    return wallets.find((w) => w.slug === slug) ?? null;
  }, [selected, wallets]);
  const selectionAggregate = useMemo(
    () => aggregateSelected(wallets, selected, fxRate),
    [wallets, selected, fxRate],
  );

  const reset = () => setFilterState(DEFAULT_FILTER);

  const sourceLabel =
    selected.size === 0
      ? "all"
      : singleSelectedWallet?.label ?? `${selected.size} selected`;

  return (
    <AppShell header={<TerminalTopBar />} ticker={<TerminalTicker />}>
      <div className="flex h-full min-h-0 flex-col gap-3">
        <PortfolioCompactBar
          selected={selected}
          onToggleSource={toggleSource}
          onSelectAll={selectAll}
          expanded={expanded}
          onToggle={() => setExpanded((e) => !e)}
        />
        {expanded && (
          <WalletStrip
            selected={selected}
            onToggleSource={toggleSource}
            onSelectAll={selectAll}
          />
        )}

        <div
          className="grid min-h-0 flex-1 gap-3 overflow-hidden"
          style={{ gridTemplateColumns: railCollapsed ? "1fr 36px" : "1fr 300px" }}
        >
          <div className="flex min-h-0 flex-col gap-3 overflow-hidden">
            {singleSelectedWallet && (
              <SourceSpotlight wallet={singleSelectedWallet} onClear={selectAll} />
            )}
            {selected.size > 1 && (
              <SourceSpotlight wallet={selectionAggregate} onClear={selectAll} />
            )}

            <FilterBar
              filter={filter}
              setFilter={setFilter}
              counts={counts}
              view={view}
              onViewChange={setView}
            />

            <SummaryBar
              filter={filter}
              source={selected.size === 0 ? "all" : "selection"}
              sourceLabel={sourceLabel}
              shownCount={filtered.length}
              totalCount={allHoldings.length}
              shownValue={shownValue}
              grandValue={grandValue}
              onReset={reset}
            />

            <div className="min-h-0 flex-1 overflow-hidden">
              {view === "tree" ? (
                <Treemap holdings={filtered} />
              ) : (
                <Ledger
                  holdings={filtered}
                  query={filter.query.trim()}
                  sortBy={filter.sortBy}
                  sortDir={filter.sortDir}
                  onSort={(sortBy, sortDir) => setFilter({ sortBy, sortDir })}
                />
              )}
            </div>
          </div>

          <RebalanceRail collapsed={railCollapsed} onToggle={toggleRail} />
        </div>
      </div>
    </AppShell>
  );
}
