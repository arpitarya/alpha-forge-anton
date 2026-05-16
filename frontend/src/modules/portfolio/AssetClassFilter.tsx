"use client";

import { clsx } from "clsx";
import {
  ASSET_BUCKETS,
  type AssetClassBucket,
  type AssetClassCounts,
  EQUITY_SUBS,
  type EquitySub,
} from "./portfolio.filter";

export interface AssetClassFilterProps {
  assetClass: AssetClassBucket;
  equitySub: EquitySub;
  counts: AssetClassCounts;
  onChange: (cls: AssetClassBucket, sub: EquitySub) => void;
}

/**
 * Hi-Fi `.pf-chips` — top-level asset class chips (All · Equity ▾ · MF/ETF · Gold)
 * with a collapsible Equity sub-filter that slides in inline when Equity is active.
 */
export function AssetClassFilter({ assetClass, equitySub, counts, onChange }: AssetClassFilterProps) {
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
      {ASSET_BUCKETS.map((a) => {
        const c = counts.cls[a.id] ?? 0;
        if (a.id !== "all" && c === 0) return null;
        const active = assetClass === a.id;
        return (
          <ChipGroup
            key={a.id}
            id={a.id}
            label={a.label}
            count={c}
            active={active}
            hasSub={a.hasSub}
            equityOpen={!!a.hasSub && assetClass === "equity"}
            equitySub={equitySub}
            equityCounts={counts.sub}
            onChange={onChange}
          />
        );
      })}
    </div>
  );
}

interface ChipGroupProps {
  id: AssetClassBucket;
  label: string;
  count: number;
  active: boolean;
  hasSub?: boolean;
  equityOpen: boolean;
  equitySub: EquitySub;
  equityCounts: Record<EquitySub, number>;
  onChange: (cls: AssetClassBucket, sub: EquitySub) => void;
}

function ChipGroup({
  id,
  label,
  count,
  active,
  hasSub,
  equityOpen,
  equitySub,
  equityCounts,
  onChange,
}: ChipGroupProps) {
  return (
    <>
      <button
        type="button"
        onClick={() => onChange(id, "all")}
        title={hasSub ? "Equity — expand for India / US / INVIT·REIT" : undefined}
        className={clsx(
          "inline-flex flex-shrink-0 items-center gap-1.5 whitespace-nowrap rounded-[5px] border px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] transition",
          hasSub && "pr-[7px]",
          active
            ? "border-[color:color-mix(in_srgb,var(--accent)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_12px_color-mix(in_srgb,var(--accent)_14%,transparent)]"
            : "border-[color:var(--line)] text-[color:var(--fg-3)] hover:border-[color:var(--line-hi)] hover:bg-[color:color-mix(in_srgb,var(--accent)_4%,transparent)] hover:text-[color:var(--fg)]",
        )}
      >
        <span>{label}</span>
        {hasSub && (
          <span
            aria-hidden="true"
            className={clsx(
              "inline-block text-[9px] leading-none transition-transform duration-200",
              active
                ? "rotate-0 text-[color:var(--accent)] opacity-85"
                : "-rotate-90 opacity-45",
            )}
          >
            ▾
          </span>
        )}
        <span
          className={clsx(
            "rounded-[3px] px-1.5 py-[1px] text-[9px] tracking-normal tabular-nums",
            active
              ? "bg-[color:color-mix(in_srgb,var(--accent)_18%,transparent)] text-[color:var(--accent)]"
              : "bg-[color:var(--surface-lo)] text-[color:var(--fg-3)]",
          )}
        >
          {count}
        </span>
      </button>

      {hasSub && (
        <div
          className={clsx(
            "inline-flex flex-shrink-0 items-center gap-[5px] overflow-hidden",
            "transition-[max-width,opacity,padding] duration-300 ease-out",
            equityOpen ? "max-w-[520px] pl-[5px] opacity-100" : "max-w-0 pl-0 opacity-0",
          )}
        >
          <span className="mx-1 my-1 h-5 w-px flex-shrink-0 self-stretch bg-[linear-gradient(180deg,transparent,color-mix(in_srgb,var(--accent)_35%,transparent),transparent)]" />
          {EQUITY_SUBS.map((s) => {
            const sc = equityCounts[s.id] ?? 0;
            if (s.id !== "all" && sc === 0) return null;
            const sActive = equitySub === s.id;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => onChange("equity", s.id)}
                tabIndex={equityOpen ? 0 : -1}
                className={clsx(
                  "inline-flex flex-shrink-0 items-center gap-[5px] whitespace-nowrap rounded-[5px] border px-2 py-1 font-mono text-[9.5px] uppercase tracking-[0.12em] transition",
                  sActive
                    ? "border-solid border-[color:color-mix(in_srgb,var(--accent)_55%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)] text-[color:var(--accent)]"
                    : "border-dashed border-[color:color-mix(in_srgb,var(--line-hi)_70%,transparent)] text-[color:var(--fg-3)] hover:border-solid hover:border-[color:color-mix(in_srgb,var(--accent)_45%,transparent)] hover:text-[color:var(--fg)]",
                )}
              >
                <span>{s.label}</span>
                <span
                  className={clsx(
                    "text-[8.5px] tabular-nums",
                    sActive ? "text-[color:var(--accent)]" : "text-[color:var(--fg-4)]",
                  )}
                >
                  {sc}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </>
  );
}
