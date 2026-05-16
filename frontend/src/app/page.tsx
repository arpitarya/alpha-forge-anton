import { AppShell } from "@alphaforge/solar-orb-ui";
import {
  AlphaBriefCard,
  OrbStage,
  TerminalStats,
  TerminalTicker,
  TerminalTopBar,
  WatchlistCard,
} from "@/modules/dashboard";

export default function Home() {
  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
    >
      <div className="grid h-full grid-cols-[300px_1fr_300px] grid-rows-[1fr_108px] gap-3 min-h-0">
        {/* Left: Alpha Brief */}
        <div className="row-span-2 min-h-0">
          <AlphaBriefCard />
        </div>

        {/* Center: Orb */}
        <div className="min-h-0">
          <OrbStage />
        </div>

        {/* Right: Watchlist + Risk Meter */}
        <div className="row-span-2 min-h-0">
          <WatchlistCard />
        </div>

        {/* Center bottom: Stats */}
        <div className="min-h-0">
          <TerminalStats />
        </div>
      </div>
    </AppShell>
  );
}
