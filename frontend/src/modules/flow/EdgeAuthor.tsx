"use client";

import { type FormEvent, useState } from "react";
import { authorEdge } from "./flow.api";
import type { AuthorEdgeRequest, FlowState } from "./flow.types";

/** Rule-stage authoring — edit a (template-seeded) EdgeSpec and PRE-REGISTER it to elgar.
 *  The `pre_registered_at` is server-stamped on save; a 422 means the edge is frozen by a run.
 *  This is the ONLY place new edges are created (no out-of-band EdgeSpec authoring). */
export function EdgeAuthor({
  seed,
  onAuthored,
}: {
  seed: AuthorEdgeRequest;
  onAuthored: (flow: FlowState) => void;
}) {
  const [form, setForm] = useState<AuthorEdgeRequest>(seed);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const set = (p: Partial<AuthorEdgeRequest>) => setForm((f) => ({ ...f, ...p }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      onAuthored(await authorEdge({ ...form, universe: form.universe.filter(Boolean) }));
    } catch (e2) {
      const ae = (e2 as { apiError?: { message?: string } }).apiError;
      setErr(ae?.message ?? "Pre-registration failed — the elgar store may be unreachable.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="of-author" onSubmit={submit} data-edge-author>
      <label className="of-fld">
        <span className="of-lbl">Hypothesis — what / why / how</span>
        <textarea
          required
          rows={3}
          value={form.hypothesis}
          onChange={(e) => set({ hypothesis: e.target.value })}
          placeholder="Recent winners that are financially strong outperform while the market trends up…"
        />
      </label>
      <div className="of-grid2">
        <label className="of-fld">
          <span className="of-lbl">Signal</span>
          <select value={form.signal} onChange={(e) => set({ signal: e.target.value })}>
            <option value="momentum">momentum</option>
            <option value="overfit_dayofmonth">overfit_dayofmonth (trap)</option>
          </select>
        </label>
        <label className="of-fld">
          <span className="of-lbl">Holding period (days)</span>
          <input
            type="number"
            min={1}
            value={form.holding_period_days}
            onChange={(e) => set({ holding_period_days: Number(e.target.value) })}
          />
        </label>
      </div>
      <label className="of-fld">
        <span className="of-lbl">Universe (comma-separated; blank = engine default)</span>
        <input
          value={form.universe.join(", ")}
          onChange={(e) => set({ universe: e.target.value.split(",").map((s) => s.trim()) })}
          placeholder="liquid NSE — top ~250 by traded value"
        />
      </label>
      <p className="of-author-note of-pending-lbl">
        Sizing · exits · rebalance cadence are later-stage artifacts — not part of the
        pre-registered spec (shown honest-pending in the cockpit).
      </p>
      {err && <p className="of-author-err">{err}</p>}
      <button type="submit" className="of-btn primary" disabled={busy}>
        {busy ? "Pre-registering…" : "Pre-register to elgar →"}
      </button>
    </form>
  );
}
