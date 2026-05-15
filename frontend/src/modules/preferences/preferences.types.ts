export interface PrefSectionMeta {
  id: string;
  label: string;
  badge?: string;
}

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

export type AccentSlug = "amber" | "ion" | "signal" | "violet";

export const ACCENTS: Array<{ slug: AccentSlug; name: string }> = [
  { slug: "amber",  name: "Amber"  },
  { slug: "ion",    name: "Ion"    },
  { slug: "signal", name: "Signal" },
  { slug: "violet", name: "Violet" },
];
