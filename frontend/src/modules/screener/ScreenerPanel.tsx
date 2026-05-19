"use client";

import { Card, Icon, ProgressBar, Text } from "@alphaforge-anton/ravel-ui";

const STUB_PICKS = [
  { symbol: "RELIANCE.NS", probability: 0.91, rank: 1, rsi_14: 62 },
  { symbol: "HDFCBANK.NS", probability: 0.87, rank: 2, rsi_14: 58 },
  { symbol: "INFY.NS", probability: 0.83, rank: 3, rsi_14: 55 },
  { symbol: "TCS.NS", probability: 0.79, rank: 4, rsi_14: 61 },
  { symbol: "ICICIBANK.NS", probability: 0.74, rank: 5, rsi_14: 57 },
  { symbol: "SBIN.NS", probability: 0.68, rank: 6, rsi_14: 53 },
];

export function ScreenerPanel() {
  return (
    <Card glow className="flex h-full flex-col">
      <Card.Header
        title={
          <span className="flex items-center gap-2">
            <Icon name="query_stats" size="sm" className="text-[color:var(--accent)]" />
            Screener
          </span>
        }
        right={<Text variant="tag" tone="subtle">demo</Text>}
      />

      <div className="flex flex-1 flex-col gap-1.5 overflow-y-auto pr-1">
        {STUB_PICKS.map((pick, i) => {
          const sym = pick.symbol.replace(".NS", "");
          return (
            <div
              key={pick.symbol}
              className="grid grid-cols-[28px_36px_1fr_180px] items-center gap-3 rounded-[var(--radius-sm)] px-2 py-2 transition-colors hover:bg-white/[0.03]"
            >
              <span className="font-mono text-[11px] tabular-nums text-[color:var(--fg-3)]">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="grid h-9 w-9 place-items-center rounded-[var(--radius-sm)] bg-white/5">
                <Icon name="trending_up" size="sm" className="text-[color:var(--accent)]" />
              </div>
              <div className="min-w-0">
                <Text className="block truncate text-sm font-bold tracking-tight">{sym}</Text>
                <Text variant="caption" tone="subtle">RSI {pick.rsi_14}</Text>
              </div>
              <ProgressBar value={pick.probability * 100} showPercentage className="!gap-1" />
            </div>
          );
        })}
      </div>

    </Card>
  );
}
