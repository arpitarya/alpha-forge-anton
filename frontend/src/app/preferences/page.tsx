"use client";

import { AppShell } from "@alphaforge-anton/ravel-ui";
import { TerminalTicker, TerminalTopBar } from "@/modules/dashboard";
import { PreferencesScreen } from "@/modules/preferences";

export default function PreferencesPage() {
  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
    >
      <PreferencesScreen />
    </AppShell>
  );
}
