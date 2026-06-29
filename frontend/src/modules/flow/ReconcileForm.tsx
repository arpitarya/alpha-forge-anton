"use client";

import { useState } from "react";
import type { Fill } from "./flow.live.types";

/** Manual fill entry — you enter what you ACTUALLY got filled at (no broker call). The panel
 *  reconciles it into true P&L vs the plan. One aggregate position keeps the slice simple. */
export function ReconcileForm({ onReconcile }: { onReconcile: (fills: Fill[]) => void }) {
  const [f, setF] = useState<Fill>({ symbol: "", qty: 0, buy_price: 0, fees: 0, last_price: 0 });
  const set = (p: Partial<Fill>) => setF((x) => ({ ...x, ...p }));

  return (
    <div className="of-reconcile" data-reconcile-form>
      <div className="of-sub">Reconcile · enter your actual fills</div>
      <div className="of-grid4">
        <input
          placeholder="symbol"
          value={f.symbol}
          onChange={(e) => set({ symbol: e.target.value })}
        />
        <input
          type="number"
          placeholder="qty"
          onChange={(e) => set({ qty: Number(e.target.value) })}
        />
        <input
          type="number"
          placeholder="buy ₹"
          onChange={(e) => set({ buy_price: Number(e.target.value) })}
        />
        <input
          type="number"
          placeholder="now ₹"
          onChange={(e) => set({ last_price: Number(e.target.value) })}
        />
      </div>
      <button
        type="button"
        className="of-btn"
        data-reconcile
        disabled={!f.qty || !f.buy_price}
        onClick={() => onReconcile([f])}
      >
        Reconcile true P&L →
      </button>
    </div>
  );
}
