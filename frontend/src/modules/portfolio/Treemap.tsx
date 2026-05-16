"use client";

import { Text, TreemapCell } from "@alphaforge/solar-orb-ui";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import type { HoldingDTO } from "./portfolio.types";
import { squarify } from "./treemap.utils";

const GAP = 3;

export function Treemap({ holdings }: { holdings: HoldingDTO[] }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    // Read initial size immediately — ResizeObserver only fires on *changes*
    // so a fully-laid-out flex child never triggers the callback on first observe.
    const initial = el.getBoundingClientRect();
    setSize({ w: initial.width, h: initial.height });
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect;
      setSize({ w: r.width, h: r.height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const cells = useMemo(() => {
    if (!size.w || !size.h || !holdings.length) return [];
    const sorted = [...holdings].sort((a, b) => b.current_value - a.current_value);
    // Square-root scale dampens the dominance of outsized positions so every
    // tile stays readable. Raw values make the top holding eat 50%+ of canvas.
    const scaled = sorted.map((h) => Math.max(0, Math.sqrt(h.current_value)));
    const rects = squarify(scaled, 0, 0, size.w, size.h);
    return sorted.map((h, i) => ({ ...rects[i], h }));
  }, [holdings, size.w, size.h]);

  // The ref div is always rendered so useLayoutEffect's ResizeObserver stays
  // attached regardless of whether holdings are loaded yet. If holdings is
  // empty, we overlay the empty state inside the same container.
  return (
    <div
      ref={ref}
      className="relative h-full overflow-hidden rounded-[10px] border border-[color:var(--line)]"
      style={{ background: "color-mix(in srgb, var(--surface) 88%, transparent)" }}
    >
      {!holdings.length ? (
        <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center">
          <Text variant="title">No positions match these filters</Text>
          <Text variant="body-sm" tone="subtle">
            Try widening the sector, clearing the search, or syncing a broker source.
          </Text>
        </div>
      ) : (
        cells.map(({ left, top, width, height, h }) => {
          const w = Math.max(0, width - GAP);
          const ch = Math.max(0, height - GAP);
          const big = w * ch > 28000;
          return (
            <TreemapCell
              key={`${h.source}-${h.symbol}-${h.isin ?? ""}`}
              symbol={h.symbol}
              sublabel={`${h.sector ?? h.asset_class} · ₹${Math.round(h.current_value).toLocaleString("en-IN")}`}
              value={`${h.pnl >= 0 ? "+" : "−"}₹${Math.abs(Math.round(h.pnl)).toLocaleString("en-IN")}`}
              change={`${h.pnl_pct >= 0 ? "+" : ""}${h.pnl_pct.toFixed(2)}%`}
              pnlPct={h.pnl_pct}
              big={big}
              style={{ left, top, width: w, height: ch }}
            />
          );
        })
      )}
    </div>
  );
}
