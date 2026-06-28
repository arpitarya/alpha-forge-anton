"use client";

import { useEffect, useState } from "react";
import type { Objective } from "@/modules/contracts";
import { GoalsScore } from "./GoalsScore";
import { GoalsStructure } from "./GoalsStructure";
import { fetchEdgeSummary, fetchMandate } from "./goals.api";
import { GOALS_LIVE_MOCK, type GoalsLive, OBJECTIVE_MOCK } from "./goals.mock";

/**
 * The editable north-star (Goals surface), wired to REAL data: the mandate comes
 * from the elgar store (GET /mandate), the edge-library band from the discovery
 * journal (GET /edges/summary). Leads with Calmar + the drawdown guard; the live
 * Calmar / drawdown / funding stay honest-pending (null) until a realised-P&L
 * source exists — never a faked number. Mock is only the typed loading fallback.
 * This is the ONLY place the objective is editable; "Propose change →" routes a
 * prompt into chat → confirm card → elgar, never a silent write.
 */
export function GoalsPanel({ onPropose }: { onPropose: (prompt: string) => void }) {
  const [obj, setObj] = useState<Objective>(OBJECTIVE_MOCK);
  const [live, setLive] = useState<GoalsLive>(GOALS_LIVE_MOCK);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [mandate, summary] = await Promise.all([fetchMandate(), fetchEdgeSummary()]);
        if (!alive) return;
        setObj(mandate);
        setLive({
          calmar: null, // honest-pending — no realised-P&L source yet (Gate-4 paper)
          current_dd: null,
          edges: summary.live, // edges promoted to capital — 0 for now
          edges_target: "2–3",
          tested: summary.tested,
          killed: summary.killed,
          kill_rate: summary.kill_rate,
        });
      } catch {
        /* keep the mock loading shape — never fake live numbers */
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div data-goals>
      <GoalsScore obj={obj} live={live} />
      <GoalsStructure obj={obj} live={live} />

      <div className="of-actions">
        <button
          type="button"
          className="of-btn primary"
          onClick={() =>
            onPropose(
              "I'd like to change my objective (Calmar target / drawdown guard / capital structure). Walk me through the trade-offs and propose the edit.",
            )
          }
        >
          Propose change →
        </button>
        <button
          type="button"
          className="of-why"
          onClick={() => onPropose("Why is my objective showing pending?")}
        >
          Why pending?
        </button>
      </div>
    </div>
  );
}
