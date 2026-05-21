"use client";

import { clsx } from "clsx";
import { useMemo } from "react";
import { useWallets } from "./portfolio.query";
import { aggregateSelected, fmtINRShort, walletBrand } from "./wallet.utils";

export interface PortfolioCompactBarProps {
  /** Set of selected broker slugs. Empty set = "All" (every wallet aggregated). */
  selected: ReadonlySet<string>;
  onToggleSource: (slug: string) => void;
  onSelectAll: () => void;
  expanded: boolean;
  onToggle: () => void;
}

/**
 * Hi-Fi `.pf-summary-bar` — slim always-visible row stacking TOTAL · INVESTED ·
 * P&L · XIRR with the per-broker wallet pills, plus a "More/Less" toggle that
 * reveals the full WalletStrip stat cards beneath.
 *
 * Totals reflect the current selection (empty = all). Click a pill to toggle
 * that broker; click "All" to clear the selection.
 */
export function PortfolioCompactBar({
  selected,
  onToggleSource,
  onSelectAll,
  expanded,
  onToggle,
}: PortfolioCompactBarProps) {
  const { data: walletsData } = useWallets();
  const wallets = walletsData?.wallets ?? [];

  const agg = useMemo(() => aggregateSelected(wallets, selected), [wallets, selected]);
  const allActive = selected.size === 0;
  const totalValue = agg.holdings_value;
  const pnl = agg.pnl;
  const pnlPct = agg.pnl_pct;
  const invested = totalValue - pnl;
  const pnlCls = pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  // XIRR is not yet computed end-to-end; reuse pnl_pct as a placeholder
  // (consistent with PortfolioHeader's xirrPlaceholder).
  const xirr = pnlPct;
  const xirrCls = xirr >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";

  return (
    <div
      data-component="PortfolioCompactBar"
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

      <div
        data-component="CompactBar.Totals"
        className="flex min-w-0 flex-[2] items-center gap-[18px] overflow-x-auto overflow-y-hidden px-1 py-0.5 tabular-nums [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
        style={{
          maskImage:
            "linear-gradient(90deg,transparent 0,#000 14px,#000 calc(100% - 14px),transparent 100%)",
          WebkitMaskImage:
            "linear-gradient(90deg,transparent 0,#000 14px,#000 calc(100% - 14px),transparent 100%)",
        }}
      >
        <span className="inline-flex flex-shrink-0 items-baseline gap-1.5 whitespace-nowrap">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">TOTAL</span>
          <span className="text-[15px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">
            {fmtINRShort(totalValue)}
          </span>
        </span>
        <span className="h-5 w-px flex-shrink-0 self-center bg-[color:var(--line)]" />
        <span className="inline-flex flex-shrink-0 items-baseline gap-1.5 whitespace-nowrap">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">INVESTED</span>
          <span className="text-[15px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">
            {fmtINRShort(invested)}
          </span>
        </span>
        <span className="h-5 w-px flex-shrink-0 self-center bg-[color:var(--line)]" />
        <span className="inline-flex flex-shrink-0 items-baseline gap-1.5 whitespace-nowrap">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">P&amp;L</span>
          <span className={clsx("text-[15px] font-medium tracking-[-0.005em]", pnlCls)}>
            {pnl >= 0 ? "+" : "−"}
            {fmtINRShort(Math.abs(pnl))}
          </span>
          <span className={clsx("font-mono text-[10px] tracking-[0.04em]", pnlCls)}>
            ({pnl >= 0 ? "+" : ""}
            {pnlPct.toFixed(1)}%)
          </span>
        </span>
        <span className="h-5 w-px flex-shrink-0 self-center bg-[color:var(--line)]" />
        <span className="inline-flex flex-shrink-0 items-baseline gap-1.5 whitespace-nowrap">
          <span className="font-mono text-[9px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">XIRR</span>
          <span className={clsx("text-[15px] font-medium tracking-[-0.005em]", xirrCls)}>
            {xirr >= 0 ? "+" : ""}
            {xirr.toFixed(1)}%
          </span>
        </span>
      </div>

      <fieldset
        data-component="CompactBar.Brokers"
        className="ml-auto flex min-w-0 flex-1 basis-[260px] items-center gap-1 overflow-x-auto overflow-y-hidden border-0 border-l border-solid border-[color:var(--line)] p-0 pl-2 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
      >
        <legend className="sr-only">Wallets (multi-select)</legend>
        <WalletPill
          slug="all"
          label="All"
          short="ALL"
          value={fmtINRShort(agg.holdings_value)}
          pnl={pnl}
          pnlPct={pnlPct}
          grad={walletBrand("all").grad}
          active={allActive}
          onClick={onSelectAll}
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
              pnl={w.pnl}
              pnlPct={w.pnl_pct}
              grad={brand.grad}
              active={selected.has(w.slug)}
              onClick={() => onToggleSource(w.slug)}
            />
          );
        })}
      </fieldset>
    </div>
  );
}

interface WalletPillProps {
  slug: string;
  label: string;
  short: string;
  value: string;
  pnl: number;
  pnlPct: number;
  grad: [string, string];
  active: boolean;
  onClick: () => void;
}

function WalletPill({ label, short, value, pnl, pnlPct, grad, active, onClick }: WalletPillProps) {
  const pnlCls = pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  return (
    <button
      type="button"
      data-component="WalletPill"
      data-broker={short.toLowerCase()}
      aria-pressed={active}
      onClick={onClick}
      title={`${label} · ${value} · ${pnl >= 0 ? "+" : "−"}${fmtINRShort(Math.abs(pnl))} (${pnl >= 0 ? "+" : ""}${pnlPct.toFixed(2)}%)`}
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
      <span
        className={clsx(
          "whitespace-nowrap font-mono text-[10px] tabular-nums tracking-[0.02em]",
          pnlCls,
        )}
      >
        {pnl >= 0 ? "+" : ""}
        {pnlPct.toFixed(1)}%
      </span>
    </button>
  );
}
