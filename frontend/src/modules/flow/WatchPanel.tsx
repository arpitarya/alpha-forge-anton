"use client";

import { clsx } from "clsx";
import { useState } from "react";
import { DecayKillBlock } from "./DecayKillBlock";
import { decayKill, fetchWatch } from "./flow.watch.api";
import type { Observation, RetirementRecord, WatchState } from "./flow.watch.types";

/** Watch stage — a deterministic decay monitor. Log the live edge's realized periods; the
 *  monitor flags decay (expectancy collapse, a −12/−20 drawdown breach, a losing streak) and, when
 *  it has decayed, offers a decay-kill that retires the edge (journaled to elgar). $0, no LLM. */
export function WatchPanel({ edgeId }: { edgeId: string }) {
  const [obs, setObs] = useState<Observation[]>([]);
  const [st, setSt] = useState<WatchState | null>(null);
  const [pct, setPct] = useState("");
  const [retired, setRetired] = useState<RetirementRecord | null>(null);

  async function add() {
    if (!pct.trim()) return;
    const next = [...obs, { period: `P${obs.length + 1}`, return_pct: Number(pct) }];
    setObs(next);
    setPct("");
    setSt(await fetchWatch(edgeId, next).catch(() => null));
  }

  async function kill(reason: string) {
    setRetired(await decayKill(edgeId, obs, reason).catch(() => null));
  }

  if (retired)
    return (
      <p className="of-decided" data-retired>
        <strong>RETIRED</strong> · decay-kill journaled to elgar — {retired.reason}
      </p>
    );

  return (
    <div className="of-watch" data-watch-panel>
      <div className="of-reconcile">
        <div className="of-sub">Log realized periods (net return %)</div>
        <div className="of-actions">
          <input
            type="number"
            value={pct}
            placeholder="period return %"
            onChange={(e) => setPct(e.target.value)}
          />
          <button type="button" className="of-btn" data-add-period onClick={add}>
            Add period →
          </button>
        </div>
      </div>

      {st && (
        <div className="of-watch-out" data-watch-out data-verdict={st.verdict}>
          <div className="of-watch-stats">
            <span>
              expectancy <strong>{st.realized_expectancy}%</strong>
            </span>
            <span>
              hit-rate <strong>{Math.round(st.hit_rate * 100)}%</strong>
            </span>
            <span>
              max DD <strong className={st.max_dd <= -12 ? "neg" : ""}>{st.max_dd}%</strong>
            </span>
            <span className={clsx("of-chip", st.verdict === "decayed" && "bad")} data-verdict-chip>
              {st.verdict}
            </span>
          </div>
          {st.signals.map((s) => (
            <div key={s.name} className="of-rt-obj" data-decay={s.severity}>
              <span className={`of-sev ${s.severity}`}>{s.severity}</span>
              <div>
                <strong>{s.name}</strong>
                {s.detail && <p>{s.detail}</p>}
              </div>
            </div>
          ))}
          {st.kill_recommended && <DecayKillBlock onKill={kill} />}
        </div>
      )}
    </div>
  );
}
