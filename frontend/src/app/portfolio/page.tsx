"use client";

import { AppShell } from "@alphaforge/solar-orb-ui";
import { useMemo, useState } from "react";
import { TerminalTicker, TerminalTopBar, TerminalVoice } from "@/modules/dashboard";
import type { FilterState } from "@/modules/portfolio";
import {
  applyFilter,
  FilterBar,
  Ledger,
  PortfolioCompactBar,
  type PortfolioView,
  RebalanceRail,
  SourceSpotlight,
  SummaryBar,
  sectorCounts,
  Treemap,
  useHoldings,
  useWallets,
  WalletStrip,
} from "@/modules/portfolio";
import { aggregateAll } from "@/modules/portfolio/wallet.utils";

const DEFAULT_FILTER: FilterState = {
  query: "",
  sector: "All",
  pnl: "all",
  sortBy: "value",
  sortDir: "desc",
};

export default function PortfolioPage() {
  const [view, setView] = useState<PortfolioView>("tree");
  const [source, setSource] = useState<string>("all");
  const [expanded, setExpanded] = useState<boolean>(false);
  const [filter, setFilterState] = useState<FilterState>(DEFAULT_FILTER);
  const setFilter = (patch: Partial<FilterState>) => setFilterState((f) => ({ ...f, ...patch }));

  const { data: holdingsData } = useHoldings(source === "all" ? undefined : source);
  const { data: walletsData } = useWallets();
  const allHoldings = holdingsData?.holdings ?? [];

  const sectors = useMemo(() => {
    const set = new Set<string>(["All"]);
    for (const h of allHoldings) set.add(h.sector ?? "Other");
    return ["All", ...[...set].filter((s) => s !== "All").sort()];
  }, [allHoldings]);

  // Sector counts respect search + pnl (so chips show what's left).
  const counts = useMemo(() => {
    const base = applyFilter(allHoldings, { ...filter, sector: "All" });
    return sectorCounts(base);
  }, [allHoldings, filter]);

  const filtered = useMemo(() => applyFilter(allHoldings, filter), [allHoldings, filter]);
  const shownValue = useMemo(() => filtered.reduce((s, h) => s + h.current_value, 0), [filtered]);
  const grandValue = useMemo(
    () => allHoldings.reduce((s, h) => s + h.current_value, 0),
    [allHoldings],
  );

  const wallets = walletsData?.wallets ?? [];
  const activeWallet = useMemo(() => {
    if (source === "all") return aggregateAll(wallets);
    return wallets.find((w) => w.slug === source) ?? null;
  }, [source, wallets]);

  const reset = () => setFilterState(DEFAULT_FILTER);

  return (
    <AppShell header={<TerminalTopBar />} ticker={<TerminalTicker />} footer={<TerminalVoice />}>
      <div className="flex h-full min-h-0 flex-col gap-3">
        <PortfolioCompactBar
          source={source}
          onSourceChange={setSource}
          expanded={expanded}
          onToggle={() => setExpanded((e) => !e)}
        />
        {expanded && <WalletStrip source={source} onChange={setSource} />}

        <div className="grid min-h-0 flex-1 grid-cols-[1fr_300px] gap-3 overflow-hidden">
          <div className="flex min-h-0 flex-col gap-3 overflow-hidden">
            {source !== "all" && activeWallet && (
              <SourceSpotlight wallet={activeWallet} onClear={() => setSource("all")} />
            )}

            <FilterBar
              filter={filter}
              setFilter={setFilter}
              sectors={sectors}
              counts={counts}
              view={view}
              onViewChange={setView}
            />

            <SummaryBar
              filter={filter}
              source={source}
              sourceLabel={activeWallet?.label ?? source}
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

          <RebalanceRail />
        </div>
      </div>
    </AppShell>
  );
}
