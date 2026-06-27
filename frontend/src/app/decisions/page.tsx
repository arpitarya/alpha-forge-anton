"use client";

import { AppShell } from "@alphaforge-anton/solar-ui";
import { TerminalTicker, TerminalTopBar } from "@/modules/dashboard";
import { CALIBRATION_MOCK, DECISIONS_MOCK, DecisionsLedger } from "@/modules/decisions";

/**
 * Decisions — the replayable prove-it ledger. Every proposal Orff put in front of
 * you, the downside it showed, your call, and how it resolved (cleared-cone /
 * hit-stop / open), with a deterministic REPLAY. Track U: mock + honest-pending.
 */
export default function DecisionsPage() {
  return (
    <AppShell header={<TerminalTopBar />} ticker={<TerminalTicker />}>
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <div
          className="mx-auto max-w-[820px]"
          style={{
            padding: 22,
            borderRadius: 12,
            border: "1px solid var(--line)",
            background: "color-mix(in srgb, var(--surface) 70%, transparent)",
          }}
        >
          <DecisionsLedger rows={DECISIONS_MOCK} calib={CALIBRATION_MOCK} />
        </div>
      </div>
    </AppShell>
  );
}
