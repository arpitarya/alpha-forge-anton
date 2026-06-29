"use client";

import { clsx } from "clsx";
import { useCallback, useEffect, useState } from "react";
import { fetchOrderPlan, reconcileFills } from "./flow.live.api";
import type { Fill, OrderPlan, ReconcileResult } from "./flow.live.types";
import { ReconcileForm } from "./ReconcileForm";

const inr = (n: number) => `${n < 0 ? "−" : ""}₹${Math.abs(Math.round(n)).toLocaleString("en-IN")}`;

/** Live stage — the EXACT orders for YOU to place + true-P&L reconciliation. Orff NEVER places
 *  an order or auto-executes (the hard invariant): the orders are copy-only and fills are entered
 *  by hand. The staged −12 / −20 guard lights from your real P&L. Unlocks only after approval. */
export function LivePanel({ edgeId }: { edgeId: string }) {
  const [plan, setPlan] = useState<OrderPlan | null>(null);
  const [res, setRes] = useState<ReconcileResult | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setPlan(await fetchOrderPlan(edgeId));
    } catch (e) {
      setErr(
        (e as { apiError?: { message?: string } }).apiError?.message ?? "Approve the edge first.",
      );
    }
  }, [edgeId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function reconcile(fills: Fill[]) {
    setRes(await reconcileFills(edgeId, fills).catch(() => null));
  }

  if (err) return <p className="of-pending-lbl">{err}</p>;
  if (!plan) return <p className="of-pending-lbl">Preparing the order plan…</p>;

  return (
    <div className="of-live" data-live-panel>
      <div className="of-noauto" data-noauto>
        ⚠ Orff never places an order — copy each line into your broker yourself.
      </div>
      <div className="of-orders" data-order-plan>
        {plan.orders.map((o) => (
          <div key={o.label} className={clsx("of-order", `k-${o.kind}`)} data-order={o.kind}>
            <span className="side">{o.side}</span>
            <span className="lbl">{o.label}</span>
            {o.notional > 0 && <span className="amt">{inr(o.notional)}</span>}
          </div>
        ))}
      </div>
      <ol className="of-checklist">
        {plan.checklist.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ol>

      <ReconcileForm onReconcile={reconcile} />
      {res && (
        <div
          className={clsx("of-recon-out", `g-${res.guard}`)}
          data-recon-out
          data-guard={res.guard}
        >
          <span>
            invested <strong>{inr(res.invested)}</strong> · now{" "}
            <strong>{inr(res.current_value)}</strong>
          </span>
          <span>
            true P&L <strong className={res.pnl < 0 ? "neg" : "pos"}>{inr(res.pnl)}</strong> (
            {res.pnl_pct}%) · slippage {inr(res.slippage)}
          </span>
          <span className="of-guard-line" data-guard-msg>
            {res.notes[0]}
          </span>
        </div>
      )}
    </div>
  );
}
