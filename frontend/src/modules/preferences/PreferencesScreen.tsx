"use client";

import { useTheme } from "@alphaforge-anton/ravel-ui";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { AboutSection } from "./AboutSection";
import { AccountSection } from "./AccountSection";
import { AlphaSection } from "./AlphaSection";
import { AppearanceSection } from "./AppearanceSection";
import { DisplaySection } from "./DisplaySection";
import { MarketsSection } from "./MarketsSection";
import { NotifSection } from "./NotifSection";
import { PreferencesSidebar } from "./PreferencesSidebar";
import { PrivacySection } from "./PrivacySection";
import { PREF_SECTIONS, SECTION_KEYS } from "./preferences.types";
import { DEFAULTS, type PrefDraft, usePrefStore } from "./usePrefStore";

function isDeepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a && b && typeof a === "object") {
    const ak = Object.keys(a as object);
    const bk = Object.keys(b as object);
    if (ak.length !== bk.length) return false;
    return ak.every((k) =>
      isDeepEqual((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k]),
    );
  }
  return false;
}

function modifiedCount(t: PrefDraft, secId: string): number {
  const keys = SECTION_KEYS[secId] ?? [];
  return keys.filter((k) => !isDeepEqual(t[k], DEFAULTS[k])).length;
}

// ── QuickStrip ───────────────────────────────────────────────────────────────
function QuickStrip({
  t,
  setTweak,
}: {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}) {
  const { theme, setTheme } = useTheme();

  const chips = [
    {
      label: "Theme",
      value: theme === "light" ? "Light" : "Dark",
      on: theme === "light",
      onClick: () => setTheme(theme === "light" ? "dark" : "light"),
      title: "Toggle dark/light theme",
    },
    {
      label: "Reduce motion",
      value: t.reduceMotion ? "On" : "Off",
      on: t.reduceMotion,
      onClick: () => setTweak("reduceMotion", !t.reduceMotion),
      title: "Disable ambient pulses & ticker drift",
    },
    {
      label: "Auto-hide chrome",
      value: t.chromeMode === "autohide" ? "On" : "Off",
      on: t.chromeMode === "autohide",
      onClick: () => setTweak("chromeMode", t.chromeMode === "autohide" ? "fixed" : "autohide"),
      title: "Collapse top + voice bars to a thin line",
    },
    {
      label: "Voice wake",
      value: t.voiceWake ? "Listening" : "Off",
      on: t.voiceWake,
      onClick: () => setTweak("voiceWake", !t.voiceWake),
      title: 'Listen for "Hey Alpha"',
    },
    {
      label: "After-hours",
      value: t.afterHours ? "On" : "Off",
      on: t.afterHours,
      onClick: () => setTweak("afterHours", !t.afterHours),
      title: "Include US after-hours/pre-open",
    },
  ];

  return (
    <div className="flex flex-none flex-wrap items-center gap-2 border-b border-[color:var(--line)] pb-2.5">
      <span className="font-mono text-[9px] uppercase tracking-[0.24em] text-[color:var(--fg-4)]">
        Quick
      </span>
      {chips.map((c) => (
        <button
          key={c.label}
          type="button"
          title={c.title}
          onClick={c.onClick}
          className={[
            "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] transition-all",
            c.on
              ? "border-[color:color-mix(in_srgb,var(--accent)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_9%,transparent)] text-[color:var(--accent)]"
              : "border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] text-[color:var(--fg-2)] hover:border-[color:var(--line-hi)] hover:text-[color:var(--fg)]",
          ].join(" ")}
        >
          <span
            className={[
              "h-1.5 w-1.5 flex-shrink-0 rounded-full",
              c.on
                ? "bg-[color:var(--accent)] shadow-[0_0_6px_var(--accent)]"
                : "bg-[color:var(--fg-4)]",
            ].join(" ")}
          />
          <span>{c.label}</span>
          <span className="font-mono text-[9px] uppercase tracking-[0.12em] opacity-60">
            {c.value}
          </span>
        </button>
      ))}
    </div>
  );
}

// ── Main ─────────────────────────────────────────────────────────────────────
export function PreferencesScreen() {
  const [active, setActive] = useState("appearance");
  const [query, setQuery] = useState("");
  const [matchCount, setMatchCount] = useState<number | null>(null);
  const [saved, setSaved] = useState(false);
  const [confirm, setConfirm] = useState<"all" | "section" | null>(null);

  const { t, setTweak, reset } = usePrefStore();
  const section = PREF_SECTIONS.find((s) => s.id === active) ?? PREF_SECTIONS[0];
  const activeMod = modifiedCount(t, active);

  const searchRef = useRef<HTMLInputElement>(null);
  const paneRef = useRef<HTMLDivElement>(null);

  // ── Saved pulse ──────────────────────────────────────────────────────────
  const tJson = JSON.stringify(t);
  const prevTRef = useRef(tJson);
  useEffect(() => {
    if (prevTRef.current === tJson) return;
    prevTRef.current = tJson;
    setSaved(true);
    const id = setTimeout(() => setSaved(false), 1400);
    return () => clearTimeout(id);
  }, [tJson]);

  // ── ⌘F / "/" focuses search ──────────────────────────────────────────────
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName ?? "";
      const inField = /^(input|textarea|select)$/i.test(tag);
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "f") {
        e.preventDefault();
        searchRef.current?.focus();
      } else if (e.key === "/" && !inField) {
        e.preventDefault();
        searchRef.current?.focus();
      } else if (e.key === "Escape" && document.activeElement === searchRef.current) {
        setQuery("");
        searchRef.current?.blur();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // ── Live DOM search filter ────────────────────────────────────────────────
  useLayoutEffect(() => {
    const pane = paneRef.current;
    if (!pane) return;
    const q = query.trim().toLowerCase();
    const rows = pane.querySelectorAll<HTMLElement>("[data-pref-key]");
    let visible = 0;
    rows.forEach((row) => {
      const nameEl = row.querySelector<HTMLElement>(".pref-row-name");
      const descEl = row.querySelector<HTMLElement>(".pref-row-desc");
      for (const el of [nameEl, descEl]) {
        if (!el) continue;
        if (el.dataset.orig == null) el.dataset.orig = el.textContent ?? "";
        el.innerHTML = el.dataset.orig;
      }
      if (!q) {
        row.classList.remove("!hidden");
        visible++;
        return;
      }
      const hay = `${nameEl?.dataset.orig ?? ""} ${descEl?.dataset.orig ?? ""}`.toLowerCase();
      if (hay.includes(q)) {
        row.classList.remove("!hidden");
        visible++;
        const esc = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const re = new RegExp(`(${esc})`, "ig");
        for (const el of [nameEl, descEl]) {
          if (!el) continue;
          el.innerHTML = (el.dataset.orig ?? "").replace(
            re,
            '<mark style="background:color-mix(in srgb,var(--accent) 30%,transparent);color:var(--fg);border-radius:2px;padding:0 1px">$1</mark>',
          );
        }
      } else {
        row.classList.add("!hidden");
      }
    });
    setMatchCount(q ? visible : null);
  }, [query]);

  // ── Reset current section to defaults ────────────────────────────────────
  const resetSection = useCallback(() => {
    const keys = SECTION_KEYS[active] ?? [];
    for (const k of keys) setTweak(k, DEFAULTS[k] as PrefDraft[typeof k]);
  }, [active, setTweak]);

  return (
    // h-full so the grid fills the AppShell <main> exactly
    <div className="grid h-full" style={{ gridTemplateColumns: "240px 1fr", gap: "14px" }}>
      {/* ── Sidebar ── */}
      <PreferencesSidebar
        active={active}
        onSelect={setActive}
        modifiedCount={modifiedCount}
        t={t}
      />

      {/* ── Right column: topline → quickstrip → scrolling pane ── */}
      <div className="relative flex min-h-0 flex-col gap-2">
        {/* Topline */}
        <div className="flex flex-none flex-wrap items-center gap-3 px-0.5">
          <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
            PREFERENCES ·{" "}
            <b className="font-normal text-[color:var(--accent)]">{section.label.toUpperCase()}</b>
          </span>

          {/* Search */}
          <div
            className="flex flex-1 items-center gap-2 rounded-[6px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] px-3 py-[7px] transition-all focus-within:border-[color:color-mix(in_srgb,var(--accent)_55%,transparent)] focus-within:shadow-[0_0_0_2px_color-mix(in_srgb,var(--accent)_14%,transparent)]"
            style={{ maxWidth: 320, minWidth: 160 }}
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden
              role="presentation"
              className="h-3 w-3 flex-shrink-0 fill-none stroke-current stroke-2 text-[color:var(--fg-3)]"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              ref={searchRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search settings"
              aria-label="Search preferences"
              className="min-w-0 flex-1 bg-transparent font-mono text-[11px] tracking-[0.04em] text-[color:var(--fg)] outline-none placeholder:text-[10px] placeholder:uppercase placeholder:tracking-[0.14em] placeholder:text-[color:var(--fg-3)]"
            />
            {matchCount != null && (
              <span className="font-mono text-[9px] tracking-[0.12em] text-[color:var(--accent)]">
                {matchCount} match{matchCount === 1 ? "" : "es"}
              </span>
            )}
            {query ? (
              <button
                type="button"
                aria-label="Clear search"
                onClick={() => {
                  setQuery("");
                  searchRef.current?.focus();
                }}
                className="flex h-4 w-4 items-center justify-center text-[15px] leading-none text-[color:var(--fg-3)] hover:text-[color:var(--fg)]"
              >
                ×
              </button>
            ) : (
              <span className="rounded-[3px] border border-[color:var(--line-hi)] px-1 py-px font-mono text-[9px] text-[color:var(--fg-3)]">
                /
              </span>
            )}
          </div>

          {/* Saved indicator + Reset section */}
          <div className="flex items-center gap-2">
            <span
              className={[
                "inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--fg-3)] transition-opacity duration-300",
                saved && !query ? "opacity-100" : "opacity-0",
              ].join(" ")}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-[color:var(--green)] shadow-[0_0_6px_var(--green)]" />
              Saved
            </span>
            <button
              type="button"
              disabled={activeMod === 0}
              onClick={() => setConfirm("section")}
              className="rounded-[5px] border border-[color:var(--line)] px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[color:var(--fg-3)] transition hover:border-[color:var(--accent)] hover:text-[color:var(--accent)] disabled:cursor-default disabled:opacity-30"
            >
              Reset{activeMod > 0 ? ` · ${activeMod}` : ""}
            </button>
          </div>
        </div>

        {/* Quick toggles */}
        <QuickStrip t={t} setTweak={setTweak} />

        {/* ── Scrolling content pane ── */}
        <div
          ref={paneRef}
          className="flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto pb-4 pr-1"
          style={{ scrollbarWidth: "thin", scrollbarColor: "var(--line-hi) transparent" }}
        >
          {active === "appearance" && <AppearanceSection t={t} setTweak={setTweak} />}
          {active === "display" && <DisplaySection t={t} setTweak={setTweak} />}
          {active === "markets" && <MarketsSection t={t} setTweak={setTweak} />}
          {active === "alpha" && <AlphaSection t={t} setTweak={setTweak} />}
          {active === "notif" && <NotifSection t={t} setTweak={setTweak} />}
          {active === "account" && <AccountSection t={t} setTweak={setTweak} />}
          {active === "privacy" && <PrivacySection t={t} setTweak={setTweak} />}
          {active === "about" && <AboutSection onResetAll={() => setConfirm("all")} />}

          {/* Empty search state */}
          {matchCount === 0 && (
            <div className="flex flex-col items-center gap-3 rounded-[10px] border border-dashed border-[color:var(--line-hi)] px-6 py-16 text-center">
              <div className="font-mono text-[11px] uppercase tracking-[0.24em] text-[color:var(--accent)]">
                ∅ No matches
              </div>
              <div className="text-[15px] font-medium text-[color:var(--fg)]">
                Nothing found for "{query}"
              </div>
              <p className="max-w-[340px] font-mono text-[10px] leading-[1.6] tracking-[0.04em] text-[color:var(--fg-3)]">
                Try a different keyword or browse sections with the sidebar.
              </p>
              <button
                type="button"
                onClick={() => setQuery("")}
                className="mt-1 rounded-[5px] border border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)] px-4 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--accent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_16%,transparent)]"
              >
                Clear search
              </button>
            </div>
          )}
        </div>

        {/* ── Confirm dialog (backdrop + modal) ── */}
        {confirm && (
          <div
            className="absolute inset-0 z-20 flex items-center justify-center rounded-[10px] backdrop-blur-[4px]"
            style={{ background: "color-mix(in srgb,#000 55%,transparent)" }}
          >
            {/* invisible close target */}
            <button
              type="button"
              aria-label="Close dialog"
              className="absolute inset-0 cursor-default"
              onClick={() => setConfirm(null)}
            />
            <div
              className="relative z-10 w-[380px] max-w-[90%] rounded-[10px] border border-[color:var(--line-hi)] p-6 shadow-[0_24px_60px_-10px_rgba(0,0,0,.7)]"
              style={{ background: "var(--surface)" }}
            >
              <h4 className="mb-2 text-[14px] font-medium text-[color:var(--fg)]">
                {confirm === "all" ? "Reset all preferences?" : "Reset this section?"}
              </h4>
              <p className="mb-5 font-mono text-[11px] leading-[1.65] tracking-[0.04em] text-[color:var(--fg-3)]">
                {confirm === "all"
                  ? "Restores every setting to its default. Account login and connected brokers are kept."
                  : `Restores the ${section.label} section (${activeMod} changed setting${activeMod === 1 ? "" : "s"}) to defaults. Other sections are untouched.`}
              </p>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setConfirm(null)}
                  className="rounded-[5px] border border-[color:var(--line-hi)] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.16em] text-[color:var(--fg-2)] hover:text-[color:var(--fg)]"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    if (confirm === "all") reset();
                    else resetSection();
                    setConfirm(null);
                  }}
                  className="rounded-[5px] border border-[color:color-mix(in_srgb,var(--red)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--red)_10%,transparent)] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.16em] text-[color:var(--red)] hover:bg-[color:color-mix(in_srgb,var(--red)_18%,transparent)]"
                >
                  {confirm === "all" ? "Reset everything" : "Reset section"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
