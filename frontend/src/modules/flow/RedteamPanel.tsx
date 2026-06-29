"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchRedteam, startRedteam } from "./flow.redteam.api";
import type { RedteamReport } from "./flow.redteam.types";

/** Red-team stage — the ONLY LLM call in the flow (cage-metered, OFF the number path).
 *  A two-tier critique: severity-tagged evidence objections + a forced 10th-Man dissent,
 *  plus runner-ups and tripwires. Advisory only; it gates nothing deterministic. Polls until done. */
export function RedteamPanel({ edgeId }: { edgeId: string }) {
  const [rt, setRt] = useState<RedteamReport | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const poll = useCallback(() => {
    timer.current = setTimeout(async () => {
      const r = await fetchRedteam(edgeId).catch(() => null);
      setRt(r);
      if (r && (r.phase === "queued" || r.phase === "running")) poll();
    }, 1500);
  }, [edgeId]);

  useEffect(() => {
    fetchRedteam(edgeId)
      .then((r) => {
        setRt(r);
        if (r && (r.phase === "queued" || r.phase === "running")) poll();
      })
      .catch(() => {});
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [edgeId, poll]);

  async function run() {
    setRt(await startRedteam(edgeId).catch(() => null));
    poll();
  }

  const busy = rt?.phase === "queued" || rt?.phase === "running";

  return (
    <div className="of-redteam" data-redteam data-phase={rt?.phase ?? "idle"}>
      <button
        type="button"
        className="of-btn primary"
        data-run-redteam
        disabled={busy}
        onClick={run}
      >
        {busy
          ? "Red-teaming (LLM)…"
          : rt?.phase === "done"
            ? "Re-run red-team"
            : "Run red-team (LLM) →"}
      </button>
      <p className="of-pending-lbl">
        The only LLM stage — advisory, cage-metered, off the deterministic number path.
      </p>

      {rt?.phase === "done" && (
        <>
          <div className="of-sub">Evidence critic · objections</div>
          {rt.objections.map((o) => (
            <div key={o.title} className="of-rt-obj" data-objection={o.severity}>
              <span className={`of-sev ${o.severity}`}>{o.severity}</span>
              <div>
                <strong>{o.title}</strong>
                {o.detail && <p>{o.detail}</p>}
              </div>
            </div>
          ))}
          <div className="of-sub">10th-Man · forced dissent</div>
          <p className="of-rt-tenth" data-tenth-man>
            {rt.tenth_man || "—"}
          </p>
          {rt.runner_ups.length > 0 && (
            <p className="of-rt-list">
              <span className="of-lbl">Runner-ups</span> {rt.runner_ups.join(" · ")}
            </p>
          )}
          {rt.tripwires.length > 0 && (
            <p className="of-rt-list">
              <span className="of-lbl">Tripwires</span> {rt.tripwires.join(" · ")}
            </p>
          )}
          <p className="of-pending-lbl of-rt-meter" data-meter>
            LLM · {rt.provider}/{rt.model} · spend recorded to the cage ledger
          </p>
        </>
      )}
      {rt?.phase === "failed" && <p className="of-author-err">Red-team failed — {rt.error}</p>}
      {!rt && <p className="of-pending-lbl">Not run yet — trigger the red-team critique.</p>}
    </div>
  );
}
