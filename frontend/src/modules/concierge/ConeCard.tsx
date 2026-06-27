import { FanChart, UChip } from "@/modules/forge";

/**
 * The inline prediction cone (P5–P95 fan). The worst case (red P5 line + red
 * caption figure) is loudest. Thin data fuzzes the band rather than faking
 * precision. When the feed is STALE the cone REFUSES to re-price: it shows ₹0
 * "because the feed hasn't refreshed — not because you're flat", never a fresh
 * number presented as live.
 */
export function ConeCard({ low, stale }: { low?: boolean; stale?: boolean }) {
  const fuzz = low || stale;
  return (
    <div className={`of-fan${fuzz ? " low" : ""}`} style={{ marginTop: 4 }}>
      <div className="ftop">
        <span className="of-lbl">Outcome cone · P5–P95 · 90 days</span>
        {stale ? (
          <UChip tone="warn" dashed>
            ⚠ stale — last-known, not live
          </UChip>
        ) : low ? (
          <UChip tone="warn" dashed>
            ⚠ low confidence — 14-mo only
          </UChip>
        ) : (
          <UChip tone="acc">14-mo base · 4k paths</UChip>
        )}
      </div>
      <div className="fanwrap">
        <FanChart low={fuzz} baseline={stale ? "₹0" : "₹3.2L"} />
      </div>
      <div className="of-conecap" style={{ marginTop: 8 }}>
        {stale ? (
          <span>
            worst 1-in-20 <span className="worst">₹0</span> · median <span className="med">₹0</span>{" "}
            · best 1-in-20 <span className="best">₹0</span>
            <span className="punch">
              ₹0 because the feed hasn't refreshed — not because you're flat. The cone won't
              re-price on stale data.
            </span>
          </span>
        ) : low ? (
          <span>
            worst 1-in-20 <span className="worst">≈ −₹2.4L</span> · median{" "}
            <span className="med">≈ +₹40k</span> · best 1-in-20{" "}
            <span className="best">≈ +₹1.5L</span>
            <span className="punch">
              Band is fuzzed &amp; dashed: only 14 months of history — treat the worst case as wider
              than shown.
            </span>
          </span>
        ) : (
          <span>
            worst 1-in-20 <span className="worst">≈ −₹1.4L</span> · median{" "}
            <span className="med">≈ +₹38k</span> · best 1-in-20{" "}
            <span className="best">≈ +₹96k</span>
            <span className="punch">The worst case is the number that matters.</span>
          </span>
        )}
      </div>
    </div>
  );
}
