"use client";

import { clsx } from "clsx";
import { useMemo } from "react";
import { useHoldings, useWallets } from "./portfolio.query";
import { aggregateAll, fmtINRShort, walletBrand } from "./wallet.utils";

export interface PortfolioCompactBarProps {
  source: string;
  onSourceChange: (slug: string) => void;
  expanded: boolean;
  onToggle: () => void;
}

/**
 * Hi-Fi `.pf-summary-bar` — slim always-visible row stacking TOTAL · INVESTED ·
 * P&L · XIRR with the per-broker wallet pills, plus a "More/Less" toggle that
 * reveals the full WalletStrip stat cards beneath.
 */
export function PortfolioCompactBar({
  source,
  onSourceChange,
  expanded,
  onToggle,
}: PortfolioCompactBarProps) {
  const { data: holdingsData } = useHoldings();
  const { data: walletsData } = useWallets();
  const wallets = walletsData?.wallets ?? [];
  const totals = holdingsData?.totals;

  const all = useMemo(() => aggregateAll(wallets), [wallets]);
  const pnl = totals?.pnl ?? 0;
  const pnlPct = totals?.pnl_pct ?? 0;
  const pnlCls = pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  const dayCls = all.pnl_pct >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";

  return (
    <div
      className={clsx(
        "relative flex flex-none items-stretch gap-2.5 overflow-hidden rounded-[10px] border border-[color:var(--line)] px-2.5 py-1.5",
        "bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)]",
        "after:pointer-events-none after:absolute after:left-0 after:top-0 after:h-px after:w-8 after:bg-[linear-gradient(90deg,var(--accent),transparent)] after:opacity-50 after:content-['']",
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        title={expanded ? "Collapse summary" : "Expand summary"}
        className="inline-flex flex-shrink-0 items-center gap-1.5 rounded-[5px] border border-[color:var(--line)] bg-transparent px-2.5 font-mono text-[9px] uppercase tracking-[0.2em] text-[color:var(--fg-3)] transition-colors hover:border-[color:color-mix(in_srgb,var(--accent)_40%,transparent)] hover:text-[color:var(--accent)]"
      >
        <span
          className={clsx(
            "inline-block text-[11px] text-[color:var(--accent)] transition-transform",
            expanded ? "rotate-90" : "",
          )}
        >
          ▸
        </span>
        <span>{expanded ? "Less" : "More"}</span>
      </button>

      <div className="flex flex-1 flex-wrap items-center gap-[18px] px-1 py-0.5 tabular-nums">
        <span className="inline-flex items-baseline gap-1.5">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">TOTAL</span>
          <span className="text-[15px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">
            {fmtINRShort(totals?.current_value ?? 0)}
          </span>
        </span>
        <span className="h-5 w-px self-center bg-[color:var(--line)]" />
        <span className="inline-flex items-baseline gap-1.5">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">INVESTED</span>
          <span className="text-[15px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">
            {fmtINRShort(totals?.invested ?? 0)}
          </span>
        </span>
        <span className="h-5 w-px self-center bg-[color:var(--line)]" />
        <span className="inline-flex items-baseline gap-1.5">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">P&amp;L</span>
          <span className={clsx("text-[15px] font-medium tracking-[-0.005em]", pnlCls)}>
            {pnl >= 0 ? "+" : "−"}
            {fmtINRShort(Math.abs(pnl))}
          </span>
          <span className={clsx("font-mono text-[10px] tracking-[0.04em]", pnlCls)}>
            {pnl >= 0 ? "+" : ""}
            {pnlPct.toFixed(1)}%
          </span>
        </span>
        <span className="h-5 w-px self-center bg-[color:var(--line)]" />
        <span className="inline-flex items-baseline gap-1.5">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">DAY</span>
          <span className={clsx("text-[15px] font-medium tracking-[-0.005em]", dayCls)}>
            {all.pnl_pct >= 0 ? "+" : ""}
            {all.pnl_pct.toFixed(2)}%
          </span>
        </span>
      </div>

      <div
        className="ml-auto flex max-w-[560px] flex-shrink-0 items-center gap-1 overflow-x-auto border-l border-[color:var(--line)] pl-2"
        style={{ scrollbarWidth: "none" }}
        role="tablist"
        aria-label="Wallets"
      >
        <WalletPill
          slug="all"
          label="All"
          short="ALL"
          value={fmtINRShort(all.holdings_value)}
          grad={walletBrand("all").grad}
          active={source === "all"}
          onClick={() => onSourceChange("all")}
        />
        {wallets.map((w) => {
          const brand = walletBrand(w.slug);
          return (
            <WalletPill
              key={w.slug}
              slug={w.slug}
              label={w.label}
              short={brand.short}
              value={fmtINRShort(w.holdings_value)}
              grad={brand.grad}
              active={source === w.slug}
              onClick={() => onSourceChange(w.slug)}
            />
          );
        })}
      </div>
    </div>
  );
}

interface WalletPillProps {
  slug: string;
  label: string;
  short: string;
  value: string;
  grad: [string, string];
  active: boolean;
  onClick: () => void;
}

function WalletPill({ label, short, value, grad, active, onClick }: WalletPillProps) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={clsx(
        "inline-flex flex-shrink-0 items-center gap-1.5 rounded-[6px] border px-2 py-1 transition-colors",
        active
          ? "border-[color:color-mix(in_srgb,var(--accent)_60%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_12px_color-mix(in_srgb,var(--accent)_14%,transparent)]"
          : "border-[color:var(--line)] text-[color:var(--fg-2)] hover:border-[color:var(--line-hi)] hover:bg-[color:color-mix(in_srgb,var(--accent)_4%,transparent)] hover:text-[color:var(--fg)]",
      )}
    >
      <span
        className="grid h-[18px] w-[18px] flex-shrink-0 place-items-center rounded-[4px] font-mono text-[8.5px] font-bold tracking-[0.04em] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.18),inset_0_-2px_4px_rgba(0,0,0,0.18)]"
        style={{ background: `linear-gradient(135deg, ${grad[0]}, ${grad[1]})` }}
      >
        {short}
      </span>
      <span className="whitespace-nowrap text-[11px] font-medium tracking-[-0.005em]">{label}</span>
      <span
        className={clsx(
          "whitespace-nowrap font-mono text-[10px] tabular-nums tracking-[0.02em]",
          active ? "text-[color:var(--accent)]" : "text-[color:var(--fg-3)]",
        )}
      >
        {value}
      </span>
    </button>
  );
}
