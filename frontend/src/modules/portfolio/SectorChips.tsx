"use client";

import { clsx } from "clsx";

export interface SectorChipsProps {
  sectors: string[];
  value: string;
  counts: Record<string, number>;
  onChange: (s: string) => void;
}

export function SectorChips({ sectors, value, counts, onChange }: SectorChipsProps) {
  return (
    <div
      className="flex min-w-0 flex-1 items-center gap-[5px] overflow-x-auto py-[2px] [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
      style={{
        maskImage:
          "linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%)",
        WebkitMaskImage:
          "linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%)",
      }}
    >
      {sectors.map((s) => {
        const c = counts[s] ?? 0;
        const isAll = s === "All";
        if (!isAll && c === 0) return null;
        const active = value === s;
        return (
          <button
            key={s}
            type="button"
            onClick={() => onChange(s)}
            className={clsx(
              "inline-flex flex-shrink-0 items-center gap-1.5 whitespace-nowrap rounded-[5px] border px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] transition",
              active
                ? "border-[color:color-mix(in_srgb,var(--accent)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_12px_color-mix(in_srgb,var(--accent)_14%,transparent)]"
                : "border-[color:var(--line)] text-[color:var(--fg-3)] hover:border-[color:var(--line-hi)] hover:bg-[color:color-mix(in_srgb,var(--accent)_4%,transparent)] hover:text-[color:var(--fg)]",
            )}
          >
            <span>{s}</span>
            <span
              className={clsx(
                "rounded-[3px] px-1.5 py-[1px] text-[9px] tracking-normal tabular-nums",
                active
                  ? "bg-[color:color-mix(in_srgb,var(--accent)_18%,transparent)] text-[color:var(--accent)]"
                  : "bg-[color:var(--surface-lo)] text-[color:var(--fg-3)]",
              )}
            >
              {c}
            </span>
          </button>
        );
      })}
    </div>
  );
}
