"use client";

import { useEffect, useState } from "react";
import { conePaths } from "./flow.cone";
import { fetchLatestRun } from "./flow.run.api";
import type { RunStatus } from "./flow.run.types";

const W = 320;
const H = 96;
const fmt = (v: number) => `${v >= 0 ? "+" : "−"}${Math.abs(v).toFixed(1)}`;

/** Range stage — the Gate-3 outcome cone, downside-first: the worst-case shortfall (es_p5)
 *  leads, loud and red. Renders the REAL p5/p50/p95 paths (percent space, no ₹). Honest-pending
 *  until the edge has been run this session; a stale cone refuses to present as fresh. */
export function RangeConePanel({ edgeId }: { edgeId: string }) {
  const [run, setRun] = useState<RunStatus | null>(null);

  useEffect(() => {
    let alive = true;
    fetchLatestRun(edgeId)
      .then((s) => alive && setRun(s))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, [edgeId]);

  const cone = run?.phase === "done" ? run.cone : null;
  if (!cone || cone.p50.length === 0) {
    return (
      <p className="of-pending-lbl">
        No cone yet — run the Test stage to compute the downside-first outcome cone.
      </p>
    );
  }

  const paths = conePaths(cone, W, H);
  const median = cone.p50.at(-1) ?? 0;
  const best = cone.p95.at(-1) ?? 0;

  return (
    <div className="of-range" data-range-cone data-stale={cone.stale}>
      <div className="of-range-hero">
        <span className="of-lbl">Worst 1-in-20 (ES P5) · {cone.horizon}</span>
        <span className="of-range-es" data-es>
          {fmt(cone.es_p5)}
        </span>
        <span className="of-pending-lbl">cumulative sleeve return — the number that matters</span>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="of-cone-svg"
        role="img"
        aria-label="Outcome cone P5–P95"
      >
        <title>Outcome cone — P5 to P95 band, worst case bold</title>
        <polygon points={paths.band} className="of-cone-band" />
        <polyline points={paths.p95} className="of-cone-p95" fill="none" />
        <polyline points={paths.p50} className="of-cone-p50" fill="none" />
        <polyline points={paths.p5} className="of-cone-p5" fill="none" />
      </svg>
      <div className="of-range-foot">
        <span>
          median <span className="med">{fmt(median)}</span>
        </span>
        <span>
          best 1-in-20 <span className="best">{fmt(best)}</span>
        </span>
        <span className="of-pending-lbl">conf {(cone.confidence * 100).toFixed(0)}%</span>
      </div>
      {cone.stale && (
        <p className="of-author-err">
          ⚠ stale feed — this cone will not re-price; treat as last-known.
        </p>
      )}
    </div>
  );
}
