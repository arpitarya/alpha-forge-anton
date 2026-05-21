import type { AccentName } from "@alphaforge-anton/ravel-ui";
import type { PrefDraft } from "./usePrefStore";

export interface PrefSectionMeta {
  id: string;
  label: string;
  badge?: string;
}

export const SECTION_KEYS: Record<string, Array<keyof PrefDraft>> = {
  appearance: ["density", "defaultScreen", "showCmdK", "typePair"],
  display:    ["chromeMode", "showVoice", "orbSize", "orbSpeed", "showHud", "tickerSpeed", "reduceMotion", "numJitter"],
  markets:    ["defaultExchange", "numberFormat", "currency", "afterHours", "refresh"],
  alpha:      ["voiceWake", "aiPersonality", "llm", "confidence", "autoRebalance", "showScreener"],
  notif:      ["notifPrice", "priceThreshold", "notifRisk", "notifSignals", "emailDigest", "email"],
  account:    ["userName", "statusLabel"],
  privacy:    ["telemetry", "crashReports", "shareTrades", "retention"],
  about:      [],
};

export const PREF_SECTIONS: PrefSectionMeta[] = [
  { id: "appearance", label: "Appearance",    badge: "Theme" },
  { id: "display",    label: "Display",       badge: "Orb"   },
  { id: "markets",    label: "Markets",       badge: "NSE"   },
  { id: "alpha",      label: "Alpha AI",      badge: "Beta"  },
  { id: "notif",      label: "Notifications"                  },
  { id: "account",    label: "Account"                        },
  { id: "privacy",    label: "Privacy"                        },
  { id: "about",      label: "About",         badge: "0.9.4" },
];

// AccentSlug is the same union as AccentName — alias keeps consumers decoupled from ravel-ui.
export type AccentSlug = AccentName;

export const ACCENTS: Array<{ slug: AccentSlug; name: string; color: string }> = [
  { slug: "amber",   name: "Amber",   color: "#ff8f00" },
  { slug: "ion",     name: "Ion",     color: "#2ee7c2" },
  { slug: "signal",  name: "Signal",  color: "#ff3d5c" },
  { slug: "violet",  name: "Violet",  color: "#a678ff" },
  { slug: "cobalt",  name: "Cobalt",  color: "#4d7cff" },
  { slug: "acid",    name: "Acid",    color: "#bef264" },
  { slug: "plasma",  name: "Plasma",  color: "#ff4dcc" },
  { slug: "solar",   name: "Solar",   color: "#ffcc33" },
  { slug: "inferno", name: "Inferno", color: "#ff5b1f" },
  { slug: "holo",    name: "Holo",    color: "#b1a0ff" },
];
