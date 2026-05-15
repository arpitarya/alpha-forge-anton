"use client";

import { clsx } from "clsx";
import type { PnLMode } from "./portfolio.filter";

const BTN_BASE =
  "border-r border-[color:var(--line)] last:border-r-0 px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.12em] transition";
const STYLE: Record<PnLMode, { active: string; idle: string; label: string }> = {
  all: {
    active:
      "text-[color:var(--accent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] shadow-[inset_0_0_10px_color-mix(in_srgb,var(--accent)_14%,transparent)]",
    idle: "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
    label: "All",
  },
  up: {
    active:
      "text-[color:var(--green)] bg-[color:color-mix(in_srgb,var(--green)_12%,transparent)] shadow-[inset_0_0_10px_color-mix(in_srgb,var(--green)_14%,transparent)]",
    idle: "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
    label: "▴ Gain",
  },
  dn: {
    active:
      "text-[color:var(--red)] bg-[color:color-mix(in_srgb,var(--red)_12%,transparent)] shadow-[inset_0_0_10px_color-mix(in_srgb,var(--red)_14%,transparent)]",
    idle: "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
    label: "▾ Loss",
  },
};

const ORDER: PnLMode[] = ["all", "up", "dn"];

export function PnLToggle({ value, onChange }: { value: PnLMode; onChange: (m: PnLMode) => void }) {
  return (
    <div className="flex flex-shrink-0 overflow-hidden rounded-[5px] border border-[color:var(--line)]">
      {ORDER.map((m) => {
        const s = STYLE[m];
        const active = value === m;
        return (
          <button
            key={m}
            type="button"
            onClick={() => onChange(m)}
            className={clsx(BTN_BASE, active ? s.active : s.idle)}
            title={m === "up" ? "Gainers only" : m === "dn" ? "Losers only" : "All positions"}
          >
            {s.label}
          </button>
        );
      })}
    </div>
  );
}
