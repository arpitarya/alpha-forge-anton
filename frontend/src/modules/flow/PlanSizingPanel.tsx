"use client";

import { clsx } from "clsx";
import { useCallback, useEffect, useState } from "react";
import { computeSizing } from "./flow.sizing.api";
import { SIZING_DEFAULTS, type SizingInputs, type SizingResult } from "./flow.sizing.types";

const inr = (n: number) =>
  n >= 1e7
    ? `₹${(n / 1e7).toFixed(2)}Cr`
    : n >= 1e5
      ? `₹${(n / 1e5).toFixed(2)}L`
      : `₹${Math.round(n).toLocaleString("en-IN")}`;

/** Plan stage — deterministic position sizing for a SURVIVING edge. Four constraints
 *  (fixed-risk · downside cap · ADV cap · fractional-Kelly); the binding (smallest) one is
 *  the recommendation. SHOWN for approval — never auto-applied, never an order. */
export function PlanSizingPanel() {
  const [form, setForm] = useState<SizingInputs>(SIZING_DEFAULTS);
  const [res, setRes] = useState<SizingResult | null>(null);
  const set = (p: Partial<SizingInputs>) => setForm((f) => ({ ...f, ...p }));

  const recompute = useCallback(async (inputs: SizingInputs) => {
    setRes(await computeSizing(inputs).catch(() => null));
  }, []);

  useEffect(() => {
    void recompute(SIZING_DEFAULTS); // compute once on mount; later recomputes are button-driven
  }, [recompute]);

  return (
    <div className="of-plan" data-plan-sizing>
      <div className="of-grid2">
        <label className="of-fld">
          <span className="of-lbl">Capital (₹)</span>
          <input
            type="number"
            value={form.capital}
            onChange={(e) => set({ capital: Number(e.target.value) })}
          />
        </label>
        <label className="of-fld">
          <span className="of-lbl">ADV — daily traded value (₹, 0 = skip)</span>
          <input
            type="number"
            value={form.adv_inr}
            onChange={(e) => set({ adv_inr: Number(e.target.value) })}
          />
        </label>
      </div>
      <button
        type="button"
        className="of-btn primary"
        data-compute-sizing
        onClick={() => void recompute(form)}
      >
        Compute sizing →
      </button>

      {res && (
        <>
          <div className="of-size-rec" data-recommended>
            <span className="of-lbl">Recommended position</span>
            <span className="of-size-big">{inr(res.recommended_notional)}</span>
            <span className="of-pending-lbl">
              {res.recommended_pct}% of capital · binding: {res.binding}
            </span>
          </div>
          <div className="of-constraints">
            {res.constraints.map((c) => (
              <div
                key={c.name}
                className={clsx("of-constraint", c.name === res.binding && "binding")}
                data-constraint={c.name}
              >
                <span className="cn">{c.name}</span>
                <span className="cv">{inr(c.notional)}</span>
                <span className="cnote">{c.note}</span>
              </div>
            ))}
          </div>
          <p className="of-pending-lbl">Shown for approval — never auto-applied, never an order.</p>
        </>
      )}
    </div>
  );
}
