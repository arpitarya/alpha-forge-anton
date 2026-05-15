"use client";

import { useTheme } from "@alphaforge/solar-orb-ui";
import { clsx } from "clsx";
import { PrefGroup } from "./PrefGroup";
import { PrefRow } from "./PrefRow";
import { ACCENTS } from "./preferences.types";

export function AppearanceSection() {
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
                  style={{
                    background: mode === "dark" ? "#0b0b0b" : "#f4f1e9",
                  }}
                >
                  <div className="absolute left-0 right-0 top-0 flex items-center gap-1 px-2 py-1.5" style={{ background: mode === "dark" ? "#1a1a1a" : "#fff" }}>
                    <i className="block h-0.5 w-3.5 rounded-sm bg-current opacity-40" style={{ color: mode === "dark" ? "#888" : "#5a564b" }} />
                    <i className="block h-0.5 w-3.5 rounded-sm bg-current opacity-40" style={{ color: mode === "dark" ? "#888" : "#5a564b" }} />
                    <i className="ml-auto block h-[3px] w-[3px] rounded-full bg-[color:var(--accent)]" />
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
          tail={<>Active <b className="font-medium text-[color:var(--accent)]">{theme.toUpperCase()}</b></>}
        />
        <PrefRow
          name="Accent color"
          desc="Tints the orb, deploy button, alerts, and HUD lines across the terminal."
          control={
            <div className="flex items-center gap-2.5">
              {ACCENTS.map((a) => (
                <button
                  type="button"
                  key={a.slug}
                  onClick={() => setAccent(a.slug)}
                  aria-label={a.name}
                  title={a.name}
                  className={clsx(
                    "relative h-[38px] w-[38px] cursor-pointer rounded-[10px] border-2 transition-transform hover:scale-110",
                    accent === a.slug
                      ? "border-transparent shadow-[0_0_0_2px_var(--fg),0_0_24px_var(--glow)]"
                      : "border-transparent",
                  )}
                  style={{
                    background:
                      a.slug === "amber" ? "linear-gradient(135deg,#FFB454,#D45A1A)"
                      : a.slug === "ion" ? "linear-gradient(135deg,#79f2d8,#0f9e85)"
                      : a.slug === "signal" ? "linear-gradient(135deg,#ff7185,#b80026)"
                      : "linear-gradient(135deg,#c6a6ff,#6a3fc7)",
                  }}
                />
              ))}
            </div>
          }
          tail={<>Active <b className="font-medium text-[color:var(--accent)]">{ACCENTS.find((a) => a.slug === accent)?.name ?? "Amber"}</b></>}
        />
      </PrefGroup>
    </>
  );
}
