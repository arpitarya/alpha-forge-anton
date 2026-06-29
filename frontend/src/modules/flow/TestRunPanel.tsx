"use client";

import { clsx } from "clsx";
import { useCallback, useEffect, useRef, useState } from "react";
import { fetchLatestRun, fetchRun, startRun } from "./flow.run.api";
import type { RunStatus } from "./flow.run.types";

/** Test stage — trigger the funnel as an async server-side job and watch the gates
 *  resolve. Deterministic, $0, LLM-free: a UI run equals the CLI run (the signature
 *  proves it). Polls the status until done; never blocks. Honest-pending before a run. */
export function TestRunPanel({ edgeId, onComplete }: { edgeId: string; onComplete: () => void }) {
  const [run, setRun] = useState<RunStatus | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const poll = useCallback(
    (jobId: string) => {
      timer.current = setTimeout(async () => {
        const s = await fetchRun(jobId).catch(() => null);
        if (!s) return;
        setRun(s);
        if (s.phase === "done" || s.phase === "failed") onComplete();
        else poll(jobId);
      }, 1500);
    },
    [onComplete],
  );

  useEffect(() => {
    fetchLatestRun(edgeId)
      .then((s) => {
        setRun(s);
        if (s && (s.phase === "queued" || s.phase === "running")) poll(s.job_id);
      })
      .catch(() => {});
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [edgeId, poll]);

  async function run_() {
    const s = await startRun(edgeId).catch(() => null);
    if (!s) return;
    setRun(s);
    poll(s.job_id);
  }

  const busy = run?.phase === "queued" || run?.phase === "running";

  return (
    <div className="of-test" data-test-run data-phase={run?.phase ?? "idle"}>
      <button
        type="button"
        className="of-btn primary"
        data-run-funnel
        disabled={busy}
        onClick={run_}
      >
        {busy
          ? "Running the funnel…"
          : run?.phase === "done"
            ? "Re-run the funnel"
            : "Run the funnel →"}
      </button>
      {run && (
        <div className="of-gates">
          {run.gates.map((g) => (
            <div key={g.gate} className={clsx("of-gate", `g-${g.state}`)} data-gate={g.gate}>
              <span className="of-gate-dot" aria-hidden />
              <span className="of-gate-lbl">
                Gate {g.gate} · {g.label}
              </span>
              <span className="of-gate-state">{busy ? "…" : g.state}</span>
            </div>
          ))}
        </div>
      )}
      {run?.phase === "done" && run.report && (
        <p className="of-test-verdict" data-verdict={run.report.verdict}>
          Verdict <strong>{run.report.verdict.toUpperCase()}</strong> ·{" "}
          {run.report.gates_passed.length}/3 gates cleared · deterministic signature{" "}
          <code>{run.signature.slice(0, 12)}</code> — a UI run equals the CLI run.
        </p>
      )}
      {run?.phase === "failed" && <p className="of-author-err">Run failed — {run.error}</p>}
      {!run && (
        <p className="of-pending-lbl">Not run yet — trigger the funnel to compute the verdict.</p>
      )}
    </div>
  );
}
