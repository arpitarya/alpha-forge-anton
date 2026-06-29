"use client";

import { AppShell } from "@alphaforge-anton/solar-ui";
import { TerminalTicker, TerminalTopBar } from "@/modules/dashboard";
import { FlowCockpit } from "@/modules/flow";

/**
 * Flow — the process-flow cockpit. The locked 8-stage operating spine
 * (Idea → Rule → Test → Range → Plan → Red-team → Approve → Live → Watch) as a view
 * over one edge's lifecycle. Stage (a): all stages render with real per-stage status;
 * edges are authored + pre-registered to elgar here (server-stamped, frozen on first run).
 * Test→Watch render honest-pending until their slices land — never a faked stage.
 */
export default function FlowPage() {
  return (
    <AppShell header={<TerminalTopBar />} ticker={<TerminalTicker />}>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <div className="mx-auto max-w-[1100px]">
          <FlowCockpit />
        </div>
      </div>
    </AppShell>
  );
}
