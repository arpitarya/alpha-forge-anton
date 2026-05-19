"use client";

import { Button, Card, Chip, ProgressBar, Text } from "@alphaforge-anton/ravel-ui";
import { useRebalance } from "@/modules/portfolio";

const CLASS_LABEL: Record<string, string> = {
  equity: "Equity",
  mutual_fund: "MF",
  etf: "ETF",
  bond: "Bond",
  gold: "Gold",
  crypto: "Crypto",
  cash: "Cash",
  other: "Other",
};

export interface RebalanceRailProps {
  collapsed: boolean;
  onToggle: () => void;
}

/**
 * Hi-Fi `.rail` — drift / target allocation panel. Collapsible: when
 * `collapsed`, renders the vertical strip (orb + vertical label + action badge)
 * from the design; otherwise the full card with toggle in the corner.
 */
export function RebalanceRail({ collapsed, onToggle }: RebalanceRailProps) {
  const { data } = useRebalance();
  const drift = data?.drift ?? [];
  const suggestions = data?.suggestions ?? [];

  if (collapsed) {
    return (
      <button
        type="button"
        onClick={onToggle}
        title="Expand Alpha rebalance"
        aria-label="Expand Alpha rebalance panel"
        className="group relative flex h-full w-9 flex-col items-center justify-between gap-3.5 self-stretch rounded-[10px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)] px-0 py-3.5 transition-colors hover:border-[color:color-mix(in_srgb,var(--accent)_45%,transparent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_6%,transparent)]"
      >
        <span className="font-mono text-[14px] leading-none text-[color:var(--fg-3)] transition-transform group-hover:-translate-x-0.5 group-hover:text-[color:var(--accent)]">
          ‹
        </span>
        <span
          aria-hidden
          className="h-3.5 w-3.5 rounded-full"
          style={{
            background:
              "radial-gradient(circle at 36% 34%, #fff, var(--accent-soft) 25%, var(--accent) 65%, transparent)",
            boxShadow: "0 0 14px var(--glow)",
          }}
        />
        <span
          className="flex flex-1 items-center font-mono text-[9.5px] tracking-[0.28em] text-[color:var(--fg-2)] group-hover:text-[color:var(--fg)]"
          style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
        >
          ALPHA · REBALANCE
        </span>
        {suggestions.length > 0 && (
          <span className="min-w-[14px] rounded-[4px] border border-[color:color-mix(in_srgb,var(--accent)_35%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_14%,transparent)] px-1.5 py-0.5 text-center font-mono text-[9px] text-[color:var(--accent)]">
            {suggestions.length}
          </span>
        )}
      </button>
    );
  }

  return (
    <Card glow className="relative flex h-full flex-col gap-4 overflow-auto">
      <button
        type="button"
        onClick={onToggle}
        title="Collapse panel"
        aria-label="Collapse panel"
        className="absolute right-2.5 top-2.5 z-10 grid h-[22px] w-[22px] place-items-center rounded-[5px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface-lo)_80%,transparent)] font-mono text-[13px] leading-none text-[color:var(--fg-3)] transition-all hover:border-[color:color-mix(in_srgb,var(--accent)_55%,transparent)] hover:bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] hover:text-[color:var(--accent)]"
      >
        ›
      </button>

      <div className="flex items-center gap-3 pr-7">
        <div
          className="h-8 w-8 rounded-full"
          style={{
            background:
              "radial-gradient(circle at 36% 34%, #fff, var(--accent-soft) 25%, var(--accent) 65%, transparent)",
            boxShadow: "0 0 20px var(--glow)",
          }}
          aria-hidden
        />
        <div className="flex flex-col">
          <Text variant="tag" tone="accent">
            Alpha · Rebalance
          </Text>
          <Text variant="title">Drift vs target allocation</Text>
        </div>
      </div>

      <div className="flex flex-col gap-3 border-l-2 border-[color:var(--accent)] pl-3">
        <Text variant="body" tone="muted">
          Targets are a balanced default (60/15/15/5/3/2). Suggestions below fire when any class
          drifts more than ±5%.
        </Text>
      </div>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <Chip key={s.action} variant="bordered">
              {s.action}
            </Chip>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-2.5">
        {drift.map((d) => (
          <ProgressBar
            key={d.asset_class}
            bidirectional
            value={d.drift_pct * 4}
            label={CLASS_LABEL[d.asset_class] ?? d.asset_class}
            showPercentage
          />
        ))}
      </div>

      <Button variant="deploy" size="lg" className="mt-auto w-full">
        Simulate &amp; backtest
      </Button>

    </Card>
  );
}
