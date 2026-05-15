"use client";

import { PrefInput, PrefSeg, PrefSlider, PrefTog } from "./PrefControls";
import { PrefGroup } from "./PrefGroup";
import { PrefRow } from "./PrefRow";
import type { PrefDraft } from "./usePrefStore";

export interface NotifSectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

export function NotifSection({ t, setTweak }: NotifSectionProps) {
  return (
    <>
      <PrefGroup num="01" title="In-app alerts">
        <PrefRow
          name="Price moves"
          desc="Toast when any watchlist symbol moves more than the threshold."
          control={<PrefTog value={t.notifPrice} onChange={(v) => setTweak("notifPrice", v)} />}
          tail={<>{t.notifPrice ? "On" : "Off"}</>}
        />
        <PrefRow
          name="Threshold"
          desc="Trigger for the price-move alert above."
          control={
            <PrefSlider
              value={t.priceThreshold}
              min={1}
              max={10}
              step={0.5}
              onChange={(v) => setTweak("priceThreshold", Number(v.toFixed(1)))}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">±{t.priceThreshold}%</b>}
        />
        <PrefRow
          name="Risk alerts"
          desc="When portfolio drift breaches your target band."
          control={<PrefTog value={t.notifRisk} onChange={(v) => setTweak("notifRisk", v)} />}
          tail={<>{t.notifRisk ? "On" : "Off"}</>}
        />
        <PrefRow
          name="New signals"
          desc="When the ML screener surfaces a new high-confidence pick."
          control={<PrefTog value={t.notifSignals} onChange={(v) => setTweak("notifSignals", v)} />}
          tail={<>{t.notifSignals ? "On" : "Off"}</>}
        />
      </PrefGroup>

      <PrefGroup num="02" title="Email">
        <PrefRow
          name="Email digest"
          desc="Summary of your day, signals, and an Alpha note."
          control={
            <PrefSeg
              value={t.emailDigest}
              options={[
                { value: "off", label: "Off" },
                { value: "daily", label: "Daily" },
                { value: "weekly", label: "Weekly" },
              ]}
              onChange={(v) => setTweak("emailDigest", v)}
            />
          }
        />
        <PrefRow
          name="Delivery"
          control={<PrefInput value={t.email} onChange={(v) => setTweak("email", v)} />}
        />
      </PrefGroup>
    </>
  );
}
