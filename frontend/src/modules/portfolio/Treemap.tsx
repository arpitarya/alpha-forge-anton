"use client";

import { Card, Text, TreemapCell } from "@alphaforge/solar-orb-ui";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import type { HoldingDTO } from "./portfolio.types";
import { squarify } from "./treemap.utils";

const GAP = 3;

export function Treemap({ holdings }: { holdings: HoldingDTO[] }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });

  useLayoutEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect;
      setSize({ w: r.width, h: r.height });
    });
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const cells = useMemo(() => {
    if (!size.w || !size.h || !holdings.length) return [];
    const sorted = [...holdings].sort((a, b) => b.current_value - a.current_value);
    const rects = squarify(
      sorted.map((h) => Math.max(0, h.current_value)),
      0,
      0,
      size.w,
      size.h,
    );
    return sorted.map((h, i) => ({ ...rects[i], h }));
  }, [holdings, size.w, size.h]);

  if (!holdings.length) {
    return (
      <Card className="flex h-full flex-col items-center justify-center gap-2">
        <Text variant="title">No positions match these filters</Text>
        <Text variant="body-sm" tone="subtle">
          Try widening the sector, clearing the search, or syncing a broker source.
        </Text>
      </Card>
    );
  }

  return (
    <Card className="relative h-full overflow-hidden !p-0">
      <div ref={ref} className="absolute inset-0">
        {cells.map(({ left, top, width, height, h }) => {
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
        })}
      </div>
    </Card>
  );
}
