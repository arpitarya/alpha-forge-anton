"use client";

import type { ReactNode } from "react";
import { ASSET_LABEL, primaryLabel } from "./ledger.utils";
import type { HoldingDTO } from "./portfolio.types";
import { currencySymbol } from "./wallet.utils";

function highlight(text: string | null | undefined, q?: string): ReactNode {
  if (!text || !q) return text ?? "";
  const t = String(text);
  const i = t.toLowerCase().indexOf(q.toLowerCase());
  if (i < 0) return t;
  return (
    <>
      {t.slice(0, i)}
      <mark className="bg-[color:color-mix(in_srgb,var(--accent)_24%,transparent)] text-[color:var(--accent)]">
        {t.slice(i, i + q.length)}
      </mark>
      {t.slice(i + q.length)}
    </>
  );
}

export function LedgerRow({ h, query }: { h: HoldingDTO; query?: string }) {
  const tone = h.pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
  const primary = primaryLabel(h);
  const secondary = primary === h.symbol ? h.name : h.symbol;
  const sym = currencySymbol(h.currency);
  const locale = h.currency === "USD" ? "en-US" : "en-IN";
  return (
    <tr
      key={`${h.source}-${h.symbol}-${h.isin ?? ""}`}
      className="border-b border-dashed border-[color:var(--line)] transition-colors hover:bg-[color:color-mix(in_srgb,var(--accent)_5%,transparent)]"
    >
      <td className="px-6 py-3 max-w-md">
        <div className="flex flex-col">
          <span className="font-semibold leading-snug">{highlight(primary, query)}</span>
          {secondary && (
            <span className="text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)] leading-snug">
              {highlight(secondary, query)}
            </span>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-right font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
        {h.source}
      </td>
      <td className="px-4 py-3 text-right font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
        {ASSET_LABEL[h.asset_class] ?? h.asset_class}
      </td>
      <td className="px-4 py-3 text-right tabular-nums">
        {h.quantity.toLocaleString(locale, { maximumFractionDigits: 4 })}
      </td>
      <td className="px-4 py-3 text-right tabular-nums">{sym}{h.avg_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-right tabular-nums">{sym}{h.last_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-right tabular-nums">
        {sym}{Math.round(h.current_value).toLocaleString(locale)}
      </td>
      <td className={`px-6 py-3 text-right tabular-nums ${tone}`}>
        {h.pnl >= 0 ? "+" : ""}{sym}{Math.round(h.pnl).toLocaleString(locale)}{" "}
        <span className="opacity-70 text-[11px]">({h.pnl_pct.toFixed(2)}%)</span>
      </td>
    </tr>
  );
}
