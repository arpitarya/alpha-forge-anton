"use client";

import { PrefSeg, PrefSlider, PrefTog } from "./PrefControls";
import { PrefGroup } from "./PrefGroup";
import { PrefRow } from "./PrefRow";
import type { PrefDraft } from "./usePrefStore";

export interface AlphaSectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

export function AlphaSection({ t, setTweak }: AlphaSectionProps) {
  return (
    <>
      <PrefGroup num="01" title="Voice & assistant" meta="Neural Interface · v2">
        <PrefRow
          name="Voice wake"
          desc={'Listen for "Hey Alpha" while the terminal is focused.'}
          control={<PrefTog value={t.voiceWake} onChange={(v) => setTweak("voiceWake", v)} />}
          tail={<>{t.voiceWake ? "Listening" : "Off"}</>}
        />
        <PrefRow
          name="Reply style"
          desc="How Alpha narrates briefs, alerts, and rebalance suggestions."
          control={
            <PrefSeg
              value={t.aiPersonality}
              options={[
                { value: "concise", label: "Concise" },
                { value: "balanced", label: "Balanced" },
                { value: "verbose", label: "Verbose" },
              ]}
              onChange={(v) => setTweak("aiPersonality", v)}
            />
          }
        />
      </PrefGroup>

      <PrefGroup num="02" title="Signals & rebalance">
        <PrefRow
          name="Signal confidence floor"
          desc="Screener picks below this score are hidden from the brief and watchlist."
          control={
            <PrefSlider
              value={t.confidence}
              min={0.5}
              max={0.95}
              step={0.05}
              onChange={(v) => setTweak("confidence", Number(v.toFixed(2)))}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">{Math.round(t.confidence * 100)}%</b>}
        />
        <PrefRow
          name="Auto-rebalance"
          desc="When Alpha drafts a rebalance plan automatically. You always confirm before it deploys."
          control={
            <PrefSeg
              value={t.autoRebalance}
              options={[
                { value: "off", label: "Off" },
                { value: "weekly", label: "Weekly" },
                { value: "monthly", label: "Monthly" },
              ]}
              onChange={(v) => setTweak("autoRebalance", v)}
            />
          }
        />
        <PrefRow
          name="Show ML screener picks on terminal"
          desc="If off, screener lives only inside the Portfolio rail."
          control={<PrefTog value={t.showScreener} onChange={(v) => setTweak("showScreener", v)} />}
          tail={<>{t.showScreener ? "On" : "Off"}</>}
        />
      </PrefGroup>
    </>
  );
}
