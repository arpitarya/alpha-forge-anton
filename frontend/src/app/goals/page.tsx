"use client";

import { AppShell } from "@alphaforge-anton/solar-ui";
import { useChat } from "@/modules/concierge";
import { TerminalTicker, TerminalTopBar } from "@/modules/dashboard";
import { GoalsAside, GoalsPanel } from "@/modules/goals";

/**
 * Goals — the editable north-star. Calmar hero + drawdown guard + self-funding +
 * capital structure. The live surface ([[GuardrailStrip]]) shows this read-only;
 * edits are proposed here and routed into chat (confirm card → elgar), never a
 * silent write. Track U: mock + honest-pending; real data lands in Phase 3.
 */
export default function GoalsPage() {
  const { submit, setOpen } = useChat();

  function propose(prompt: string) {
    setOpen(true);
    submit(prompt, { provider: "auto" });
  }

  return (
    <AppShell header={<TerminalTopBar />} ticker={<TerminalTicker />}>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <div className="mx-auto grid max-w-[1100px] grid-cols-1 gap-4 lg:grid-cols-[1.4fr_1fr]">
          <section
            style={{
              padding: 22,
              borderRadius: 12,
              border: "1px solid var(--line)",
              background: "color-mix(in srgb, var(--surface) 70%, transparent)",
            }}
          >
            <GoalsPanel onPropose={propose} />
          </section>
          <aside>
            <GoalsAside />
          </aside>
        </div>
      </div>
    </AppShell>
  );
}
