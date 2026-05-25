"use client";

import { PrefSeg, PrefSelect, PrefTog } from "@alphaforge-anton/solar-ui";
import { PrefGroup } from "@alphaforge-anton/solar-ui";
import { PrefRow } from "@alphaforge-anton/solar-ui";
import type { PrefDraft } from "./usePrefStore";

export interface MarketsSectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

export function MarketsSection({ t, setTweak }: MarketsSectionProps) {
  return (
    <>
      <PrefGroup num="01" title="Defaults">
        <PrefRow
          name="Primary exchange"
          desc="Used when you ask Alpha about a symbol without a venue."
          control={
            <PrefSelect
              value={t.defaultExchange}
              options={[
                { value: "NSE", label: "NSE — India" },
                { value: "BSE", label: "BSE — India" },
                { value: "NASDAQ", label: "NASDAQ — US" },
                { value: "NYSE", label: "NYSE — US" },
                { value: "CRYPTO", label: "Crypto · 24/7" },
              ]}
              onChange={(v) => setTweak("defaultExchange", v)}
            />
          }
        />
        <PrefRow
          name="Number format"
          desc="Indian uses lakh / crore grouping (12,84,500). Western uses thousands (1,284,500)."
          control={
            <PrefSeg
              value={t.numberFormat}
              options={[
                { value: "indian", label: "Indian" },
                { value: "western", label: "Western" },
              ]}
              onChange={(v) => setTweak("numberFormat", v)}
            />
          }
        />
        <PrefRow
          name="Show currency in"
          desc="The currency Alpha quotes net worth and P&L in."
          control={
            <PrefSeg
              value={t.currency}
              options={[
                { value: "INR", label: "INR" },
                { value: "USD", label: "USD" },
                { value: "Native", label: "Native" },
              ]}
              onChange={(v) => setTweak("currency", v)}
            />
          }
        />
        <PrefRow
          name="Include after-hours"
          desc="Reflect US after-hours and pre-open in your dashboard."
          control={<PrefTog value={t.afterHours} onChange={(v) => setTweak("afterHours", v)} />}
          tail={<>{t.afterHours ? "On" : "Off"}</>}
        />
      </PrefGroup>

      <PrefGroup num="02" title="Refresh">
        <PrefRow
          name="Tick refresh"
          desc="How often Alpha pulls fresh prices in the background."
          control={
            <PrefSeg
              value={t.refresh}
              options={[
                { value: "1s", label: "1 s" },
                { value: "5s", label: "5 s" },
                { value: "30s", label: "30 s" },
                { value: "manual", label: "Manual" },
              ]}
              onChange={(v) => setTweak("refresh", v)}
            />
          }
        />
      </PrefGroup>
    </>
  );
}
