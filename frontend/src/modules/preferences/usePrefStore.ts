"use client";

import { useEffect, useState } from "react";

// Non-wired preference state — persisted to localStorage so the UI mockup
// behaves consistently across reloads while backend wiring lands.
export interface PrefDraft {
  // Display / chrome
  chromeMode: "fixed" | "autohide";
  showVoice: boolean;
  orbSize: number;
  orbSpeed: number;
  showHud: boolean;
  tickerSpeed: number;
  reduceMotion: boolean;
  numJitter: boolean;
  // Markets
  defaultExchange: "NSE" | "BSE" | "NASDAQ" | "NYSE" | "CRYPTO";
  numberFormat: "indian" | "western";
  currency: "INR" | "USD" | "Native";
  afterHours: boolean;
  refresh: "1s" | "5s" | "30s" | "manual";
  // Alpha AI
  voiceWake: boolean;
  aiPersonality: "concise" | "balanced" | "verbose";
  confidence: number;
  autoRebalance: "off" | "weekly" | "monthly";
  showScreener: boolean;
  // Notifications
  notifPrice: boolean;
  priceThreshold: number;
  notifRisk: boolean;
  notifSignals: boolean;
  emailDigest: "off" | "daily" | "weekly";
  email: string;
  // Account
  userName: string;
  statusLabel: string;
  // Privacy
  telemetry: boolean;
  crashReports: boolean;
  shareTrades: boolean;
  retention: "30" | "90" | "365" | "all";
}

export const DEFAULTS: PrefDraft = {
  chromeMode: "fixed",
  showVoice: true,
  orbSize: 260,
  orbSpeed: 3.4,
  showHud: true,
  tickerSpeed: 48,
  reduceMotion: false,
  numJitter: true,
  defaultExchange: "NSE",
  numberFormat: "indian",
  currency: "INR",
  afterHours: false,
  refresh: "5s",
  voiceWake: true,
  aiPersonality: "balanced",
  confidence: 0.8,
  autoRebalance: "off",
  showScreener: true,
  notifPrice: true,
  priceThreshold: 3,
  notifRisk: true,
  notifSignals: true,
  emailDigest: "daily",
  email: "arjun.k@protonmail.com",
  userName: "Arjun",
  statusLabel: "LIVE · NSE",
  telemetry: true,
  crashReports: true,
  shareTrades: false,
  retention: "90",
};

const KEY = "af-prefs-draft-v1";

export function usePrefStore() {
  const [draft, setDraft] = useState<PrefDraft>(DEFAULTS);

  // Hydrate after mount to avoid SSR mismatch.
  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(KEY) : null;
      if (raw) setDraft({ ...DEFAULTS, ...JSON.parse(raw) });
    } catch {
      /* ignore corrupt persisted state */
    }
  }, []);

  // Apply body-level toggles when chrome / voice prefs change.
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.classList.toggle("chrome-autohide", draft.chromeMode === "autohide");
    document.body.classList.toggle("no-voice", !draft.showVoice);
  }, [draft.chromeMode, draft.showVoice]);

  function setTweak<K extends keyof PrefDraft>(key: K, value: PrefDraft[K]) {
    setDraft((prev) => {
      const next = { ...prev, [key]: value };
      try {
        localStorage.setItem(KEY, JSON.stringify(next));
      } catch {
        /* quota / private mode — ignore */
      }
      return next;
    });
  }

  return { t: draft, setTweak };
}
