"use client";

import { PrefSeg, PrefSlider, PrefTog } from "./PrefControls";
import { PrefGroup } from "./PrefGroup";
import { PrefRow } from "./PrefRow";
import type { PrefDraft } from "./usePrefStore";

export interface DisplaySectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

export function DisplaySection({ t, setTweak }: DisplaySectionProps) {
  return (
    <>
      <PrefGroup num="01" title="Chrome" meta="Top + Voice bars">
        <PrefRow
          name="Chrome behavior"
          desc="The slim top + voice bars appear on every screen. Auto-hide collapses them to a thin accent line — hover or focus to reveal."
          control={
            <PrefSeg
              value={t.chromeMode}
              options={[
                { value: "fixed", label: "Always visible" },
                { value: "autohide", label: "Auto-hide" },
              ]}
              onChange={(v) => setTweak("chromeMode", v)}
            />
          }
          tail={
            <b className="font-normal text-[color:var(--accent)]">
              {t.chromeMode === "autohide" ? "Hidden" : "Visible"}
            </b>
          }
        />
        <PrefRow
          name="Show voice bar"
          desc="The global Alpha voice / Deploy bar at the bottom of every screen."
          control={<PrefTog value={t.showVoice} onChange={(v) => setTweak("showVoice", v)} />}
          tail={<>{t.showVoice ? "On" : "Off"}</>}
        />
      </PrefGroup>

      <PrefGroup num="02" title="Alpha orb" meta="Stage centerpiece">
        <PrefRow
          name="Orb size"
          desc="Diameter of the central plasma sphere on the terminal."
          control={
            <PrefSlider
              value={t.orbSize}
              min={180}
              max={340}
              step={10}
              onChange={(v) => setTweak("orbSize", v)}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">{t.orbSize}px</b>}
        />
        <PrefRow
          name="Pulse speed"
          desc="Lower is calmer. Speed scales with system confidence on real data."
          control={
            <PrefSlider
              value={t.orbSpeed}
              min={1.5}
              max={6}
              step={0.1}
              onChange={(v) => setTweak("orbSpeed", Number(v.toFixed(1)))}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">{t.orbSpeed.toFixed(1)}s</b>}
        />
        <PrefRow
          name="HUD chrome"
          desc="Corner brackets, drifting stars and scanline around the orb stage."
          control={<PrefTog value={t.showHud} onChange={(v) => setTweak("showHud", v)} />}
          tail={<>{t.showHud ? "Visible" : "Hidden"}</>}
        />
      </PrefGroup>

      <PrefGroup num="03" title="Motion">
        <PrefRow
          name="Ticker speed"
          desc="Time for one full loop across the index ribbon."
          control={
            <PrefSlider
              value={t.tickerSpeed}
              min={15}
              max={90}
              step={1}
              onChange={(v) => setTweak("tickerSpeed", v)}
            />
          }
          tail={<b className="font-normal text-[color:var(--accent)]">{t.tickerSpeed}s</b>}
        />
        <PrefRow
          name="Reduce motion"
          desc="Disables ambient pulsing, scanlines, and ticker drift. Recommended for long sessions."
          control={<PrefTog value={t.reduceMotion} onChange={(v) => setTweak("reduceMotion", v)} />}
          tail={<>{t.reduceMotion ? "On" : "Off"}</>}
        />
        <PrefRow
          name="Number jitter"
          desc="Live micro-flicker on watchlist prices between real ticks."
          control={<PrefTog value={t.numJitter} onChange={(v) => setTweak("numJitter", v)} />}
          tail={<>{t.numJitter ? "On" : "Off"}</>}
        />
      </PrefGroup>
    </>
  );
}
