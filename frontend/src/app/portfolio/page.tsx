"use client";

import { AppShell } from "@alphaforge/solar-orb-ui";
import { useState } from "react";
import {
  TerminalTicker,
  TerminalTopBar,
  TerminalVoice,
} from "@/modules/dashboard";
import {
  Ledger,
  PortfolioHeader,
  type PortfolioView,
  RebalanceRail,
  Treemap,
} from "@/modules/portfolio";

export default function PortfolioPage() {
  const [view, setView] = useState<PortfolioView>("tree");

  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
      footer={<TerminalVoice />}
    >
      <div className="grid h-full grid-cols-[1fr_300px] grid-rows-[auto_1fr] gap-3 min-h-0">
        {/* Header stats strip */}
        <div className="col-span-2">
          <PortfolioHeader view={view} onViewChange={setView} />
        </div>

        {/* Main: treemap or ledger */}
        <div className="min-h-0 overflow-hidden">
          {view === "tree" ? <Treemap /> : <Ledger />}
        </div>

        {/* Right rail: rebalance */}
        <div className="min-h-0">
          <RebalanceRail />
        </div>
      </div>
    </AppShell>
  );
}
