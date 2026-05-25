"use client";

import { useTheme } from "@alphaforge-anton/solar-ui";
import { clsx } from "clsx";
import { PrefSeg, PrefSelect, PrefTog } from "@alphaforge-anton/solar-ui";
import { PrefGroup } from "@alphaforge-anton/solar-ui";
import { PrefRow } from "@alphaforge-anton/solar-ui";
import { ACCENTS } from "./preferences.types";
import type { PrefDraft } from "./usePrefStore";

export interface AppearanceSectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

// Per-design gradients for each accent swatch
const SWATCH_BG: Record<string, string> = {
  amber: "linear-gradient(135deg,#FFB454,#D45A1A)",
  ion: "linear-gradient(135deg,#79f2d8,#0f9e85)",
  signal: "linear-gradient(135deg,#ff7185,#b80026)",
  violet: "linear-gradient(135deg,#c6a6ff,#6a3fc7)",
  cobalt: "linear-gradient(135deg,#85a4ff,#1f4fd6)",
  acid: "linear-gradient(135deg,#e2ff8f,#7fa72e)",
  plasma: "linear-gradient(135deg,#ff85dc,#c41891)",
  solar: "linear-gradient(135deg,#ffdf7a,#c79100)",
  inferno: "linear-gradient(135deg,#fff066 0%,#ffba2e 22%,#ff5b1f 52%,#c01a00 78%,#3a0500 100%)",
  holo: "conic-gradient(from 210deg at 50% 50%,#ff4dcc,#ff8a3d,#ffe066,#bef264,#2ee7c2,#4d7cff,#b1a0ff,#ff4dcc)",
};

export function AppearanceSection({ t, setTweak }: AppearanceSectionProps) {
  const { theme, accent, setTheme, setAccent } = useTheme();

  return (
    <>
      <PrefGroup num="01" title="Theme" meta="Live preview">
        <PrefRow
          name="Color scheme"
          desc="Dark uses the warm-black terminal palette. Light is parchment-toned for daytime trading."
          control={
            <div className="flex gap-3">
              {(["dark", "light"] as const).map((mode) => (
                <button
                  type="button"
                  key={mode}
                  onClick={() => setTheme(mode)}
                  aria-label={mode}
                  className={clsx(
                    "relative h-[86px] w-[138px] cursor-pointer overflow-hidden rounded-[8px] border transition-transform hover:-translate-y-0.5",
                    theme === mode
                      ? "border-[color:var(--accent)] shadow-[0_0_0_1px_var(--accent),0_0_24px_var(--glow)]"
                      : "border-[color:var(--line-hi)]",
                  )}
                  style={{ background: mode === "dark" ? "#0b0b0b" : "#f4f1e9" }}
                >
                  <div
                    className="absolute left-0 right-0 top-0 flex items-center gap-1 px-2 py-1.5"
                    style={{ background: mode === "dark" ? "#1a1a1a" : "#fff" }}
                  >
                    <i
                      className="block h-0.5 w-3.5 rounded-sm bg-current opacity-40"
                      style={{ color: mode === "dark" ? "#888" : "#5a564b" }}
                    />
                    <i
                      className="block h-0.5 w-3.5 rounded-sm bg-current opacity-40"
                      style={{ color: mode === "dark" ? "#888" : "#5a564b" }}
                    />
                    <i className="ml-auto block h-[3px] w-[3px] rounded-full bg-[color:var(--accent)]" />
                  </div>
                  <div
                    className="absolute bottom-[18px] left-2 right-2 top-[18px] flex gap-1 p-1.5"
                    style={{ background: mode === "dark" ? "#0b0b0b" : "#f4f1e9" }}
                  >
                    <div
                      className="flex-1 rounded-[3px]"
                      style={{
                        background: mode === "dark" ? "#16140f" : "#fff",
                        position: "relative",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          position: "absolute",
                          left: "50%",
                          top: "50%",
                          width: "60%",
                          height: "60%",
                          borderRadius: "50%",
                          background:
                            "radial-gradient(circle at 35% 35%, var(--accent-soft), var(--accent) 60%)",
                          transform: "translate(-50%,-50%)",
                          boxShadow: "0 0 10px var(--glow)",
                        }}
                      />
                    </div>
                    <div
                      className="flex-1 rounded-[3px]"
                      style={{ background: mode === "dark" ? "#16140f" : "#fff" }}
                    />
                  </div>
                  <span
                    className="absolute bottom-1.5 left-2 font-mono text-[9px] font-semibold uppercase tracking-[0.18em]"
                    style={{ color: mode === "dark" ? "#888" : "#5a564b" }}
                  >
                    {mode}
                  </span>
                </button>
              ))}
            </div>
          }
          tail={
            <>
              Active <b className="font-normal text-[color:var(--accent)]">{theme.toUpperCase()}</b>
            </>
          }
        />
        <PrefRow
          name="Accent color"
          desc="Tints the orb, deploy button, alerts, and HUD lines across the terminal."
          control={
            <div className="flex flex-wrap items-center gap-2.5 pb-6">
              {ACCENTS.map((a) => {
                const isActive = accent === a.slug;
                return (
                  <div key={a.slug} className="relative">
                    <button
                      type="button"
                      onClick={() => setAccent(a.slug)}
                      aria-label={a.name}
                      title={a.name}
                      className={clsx(
                        "relative h-[38px] w-[38px] cursor-pointer overflow-hidden rounded-[10px] border-2 border-transparent transition-transform hover:scale-[1.08]",
                        isActive && "shadow-[0_0_0_2px_var(--fg),0_0_24px_var(--glow)]",
                      )}
                      style={{ background: SWATCH_BG[a.slug] ?? a.color }}
                    >
                      {isActive && (
                        <span
                          aria-hidden
                          className="absolute inset-0 flex items-center justify-center"
                        >
                          <svg
                            viewBox="0 0 24 24"
                            aria-hidden
                            role="presentation"
                            className="h-4 w-4 drop-shadow-[0_1px_1px_rgba(0,0,0,0.4)]"
                            fill="none"
                            stroke="white"
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M6 12.5 10 16.5 18 8" />
                          </svg>
                        </span>
                      )}
                    </button>
                    <span className="pointer-events-none absolute -bottom-5 left-1/2 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] uppercase tracking-[0.18em] text-[color:var(--fg-3)] opacity-0 transition-opacity group-hover:opacity-100 [button:hover+&]:opacity-100">
                      {a.name}
                    </span>
                  </div>
                );
              })}
            </div>
          }
          tail={
            <>
              Active{" "}
              <b className="font-normal text-[color:var(--accent)]">
                {ACCENTS.find((a) => a.slug === accent)?.name ?? "Amber"}
              </b>
            </>
          }
        />
      </PrefGroup>

      <PrefGroup num="02" title="Layout">
        <PrefRow
          prefKey="density"
          name="Density"
          desc="Compact fits more data per pane. Comfy gives charts room to breathe."
          control={
            <PrefSeg
              value={t.density}
              options={[
                { value: "compact", label: "Compact" },
                { value: "regular", label: "Regular" },
                { value: "comfy", label: "Comfy" },
              ]}
              onChange={(v) => setTweak("density", v)}
            />
          }
        />
        <PrefRow
          prefKey="defaultScreen"
          name="Default screen"
          desc="What loads after the boot sequence completes."
          control={
            <PrefSelect
              value={t.defaultScreen}
              options={[
                { value: "terminal", label: "Terminal" },
                { value: "portfolio", label: "Portfolio" },
                { value: "preferences", label: "Preferences" },
              ]}
              onChange={(v) => setTweak("defaultScreen", v)}
            />
          }
        />
        <PrefRow
          prefKey="showCmdK"
          name="Show command palette hint"
          desc="The ⌘K pill in the top bar."
          control={<PrefTog value={t.showCmdK} onChange={(v) => setTweak("showCmdK", v)} />}
          tail={<>{t.showCmdK ? "On" : "Off"}</>}
        />
      </PrefGroup>

      <PrefGroup num="03" title="Typography" meta="Space Grotesk · Space Mono">
        <PrefRow
          prefKey="typePair"
          name="Type pair"
          desc="Display + monospace pair used everywhere."
          control={
            <PrefSelect
              value={t.typePair}
              options={[
                { value: "grotesk-mono", label: "Space Grotesk × Space Mono" },
                { value: "ibm-mono", label: "IBM Plex × Plex Mono" },
                { value: "serif-mono", label: "Fraunces × Berkeley Mono" },
              ]}
              onChange={(v) => setTweak("typePair", v)}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">Default</b>}
        />
      </PrefGroup>
    </>
  );
}
