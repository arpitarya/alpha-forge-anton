"use client";

import { AppShell } from "@alphaforge/solar-orb-ui";
import { TerminalTicker, TerminalTopBar, TerminalVoice } from "@/modules/dashboard";
import { PreferencesScreen } from "@/modules/preferences";

export default function PreferencesPage() {
  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
      footer={<TerminalVoice />}
    >
      <PreferencesScreen />
    </AppShell>
  );
}
