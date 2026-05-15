"use client";

import { useState } from "react";
import { AboutSection } from "./AboutSection";
import { AccountSection } from "./AccountSection";
import { AlphaSection } from "./AlphaSection";
import { AppearanceSection } from "./AppearanceSection";
import { DisplaySection } from "./DisplaySection";
import { MarketsSection } from "./MarketsSection";
import { NotifSection } from "./NotifSection";
import { PreferencesSidebar } from "./PreferencesSidebar";
import { PrivacySection } from "./PrivacySection";
import { PREF_SECTIONS } from "./preferences.types";
import { usePrefStore } from "./usePrefStore";

export function PreferencesScreen() {
  const [active, setActive] = useState("appearance");
  const section = PREF_SECTIONS.find((s) => s.id === active) ?? PREF_SECTIONS[0];
  const { t, setTweak } = usePrefStore();

  return (
    <div className="grid h-full min-h-0 gap-3.5 overflow-hidden" style={{ gridTemplateColumns: "248px 1fr" }}>
      <PreferencesSidebar active={active} onSelect={setActive} />
      <div className="flex min-h-0 flex-col gap-3 overflow-hidden">
        <div className="flex flex-none items-center justify-between px-1 py-0.5">
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
            PREFERENCES · <b className="font-normal text-[color:var(--accent)]">{section.label.toUpperCase()}</b>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--fg-3)]">
              <span className="h-1.5 w-1.5 rounded-full bg-[color:var(--green)] shadow-[0_0_8px_var(--green)]" />
              Saved
            </span>
          </div>
        </div>
        <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto pr-1">
          {active === "appearance" && <AppearanceSection />}
          {active === "display" && <DisplaySection t={t} setTweak={setTweak} />}
          {active === "markets" && <MarketsSection t={t} setTweak={setTweak} />}
          {active === "alpha" && <AlphaSection t={t} setTweak={setTweak} />}
          {active === "notif" && <NotifSection t={t} setTweak={setTweak} />}
          {active === "account" && <AccountSection t={t} setTweak={setTweak} />}
          {active === "privacy" && <PrivacySection t={t} setTweak={setTweak} />}
          {active === "about" && <AboutSection />}
        </div>
      </div>
    </div>
  );
}
