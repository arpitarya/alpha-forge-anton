"use client";

import { clsx } from "clsx";
import { SectionIcon } from "./SectionIcon";
import { PREF_SECTIONS } from "./preferences.types";

export interface PreferencesSidebarProps {
  active: string;
  onSelect: (id: string) => void;
}

export function PreferencesSidebar({ active, onSelect }: PreferencesSidebarProps) {
  return (
    <aside
      className="relative flex flex-col gap-1 overflow-hidden rounded-[10px] border border-[color:var(--line)] px-3 py-4"
      style={{ background: "color-mix(in srgb, var(--surface) 88%, transparent)" }}
    >
      <span
        aria-hidden
        className="pointer-events-none absolute left-0 top-0 h-px w-8 opacity-60"
        style={{ background: "linear-gradient(90deg, var(--accent), transparent)" }}
      />
      <span
        aria-hidden
        className="pointer-events-none absolute left-0 top-0 h-8 w-px opacity-60"
        style={{ background: "linear-gradient(180deg, var(--accent), transparent)" }}
      />
      <div className="mb-2.5 border-b border-[color:var(--line)] px-2.5 pb-4 pt-1.5">
        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-[color:var(--accent)]">· SYSTEM</div>
        <div className="mt-1.5 text-[22px] font-medium leading-[1.05] tracking-[-0.01em]">Preferences</div>
        <div className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]">v0.9.4 · LIVE</div>
      </div>
      {PREF_SECTIONS.map((s) => {
        const isActive = active === s.id;
        return (
          <button
            type="button"
            key={s.id}
            onClick={() => onSelect(s.id)}
            className={clsx(
              "grid w-full items-center gap-3 rounded-[6px] border px-3 py-2.5 text-left font-mono text-[11px] uppercase tracking-[0.18em] transition-colors",
              isActive
                ? "border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_24px_color-mix(in_srgb,var(--accent)_12%,transparent)]"
                : "border-transparent text-[color:var(--fg-2)] hover:bg-[color:color-mix(in_srgb,var(--accent)_5%,transparent)] hover:text-[color:var(--fg)]",
            )}
            style={{ gridTemplateColumns: "18px 1fr auto" }}
          >
            <SectionIcon id={s.id} />
            <span>{s.label}</span>
            {s.badge && (
              <span
                className={clsx(
                  "rounded-[3px] px-1.5 py-0.5 font-mono text-[9px] tracking-[0.12em]",
                  isActive
                    ? "bg-[color:color-mix(in_srgb,var(--accent)_25%,transparent)] text-[color:var(--accent)]"
                    : "bg-[color:var(--line-hi)] text-[color:var(--fg-3)]",
                )}
              >
                {s.badge}
              </span>
            )}
          </button>
        );
      })}
      <div className="mt-auto border-t border-[color:var(--line)] px-2.5 pb-1 pt-3.5 font-mono text-[10px] leading-[1.7] tracking-[0.16em] text-[color:var(--fg-3)]">
        <div><span className="text-[color:var(--fg-2)]">SEAT</span> <span className="text-[color:var(--accent)]">#00142</span></div>
        <div><span className="text-[color:var(--fg-2)]">TIER</span> <span className="text-[color:var(--accent)]">PRO</span></div>
        <div><span className="text-[color:var(--fg-2)]">NODE</span> <span className="text-[color:var(--accent)]">MUMBAI_01</span></div>
      </div>
    </aside>
  );
}
