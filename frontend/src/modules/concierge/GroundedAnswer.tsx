import { Num, Www } from "@/modules/forge";
import { SOURCES } from "./proposal.mock";

export type Feed = "live" | "stale" | "error";

/**
 * The grounded answer body. LIVE = citations + what/why/how. STALE = loud badge
 * and a muted ₹0 that explicitly means "no data, not flat". ERROR = red badge,
 * forecast withheld — an error is never a fabricated answer.
 */
export function GroundedAnswer({ feed }: { feed: Feed }) {
  if (feed === "error") {
    return (
      <div>
        <div className="of-stale err solid">
          <span className="warn">✕</span> grounding error — NSE feed unreachable
        </div>
        <div className="of-stalenote">
          I won't answer this on a broken source. The option-chain feed returned{" "}
          <b>504 after 3 retries</b>, so I have <b>no grounded basis</b> for a call — and I won't
          guess one. The cone is withheld until the feed re-grounds.
        </div>
      </div>
    );
  }
  if (feed === "stale") {
    return (
      <div>
        <div className="of-stale solid">
          <span className="warn">⚠</span> stale feed — last close 15:30 IST
        </div>
        <div className="of-stalenote">
          I can't confirm today's P&amp;L. It reads{" "}
          <Num v="₹0" kind="neutral" className="of-zero" /> because the market feed hasn't refreshed
          since last close — <b>not because you're flat.</b> Treat the cone as last-known, not live.
        </div>
      </div>
    );
  }
  return (
    <div>
      <p style={{ fontSize: 13.5, lineHeight: 1.55, color: "var(--fg-2)" }}>
        Bank Nifty IV is rich into Thursday's RBI decision — front-month at the{" "}
        <strong style={{ color: "var(--fg)" }}>78th percentile</strong> of its 1-yr range
        <sup className="of-cite-ref">1</sup>, and rate-decision days have averaged a{" "}
        <strong style={{ color: "var(--fg)" }}>1.4% gap</strong> since 2023
        <sup className="of-cite-ref">2</sup>. That supports a hedged mean-reversion, with caution
        <sup className="of-cite-ref">3</sup>.
      </p>
      <div className="of-sources">
        {SOURCES.map((s) => (
          <div className="of-src" key={s.n}>
            <span className="num">{s.n}</span>
            <span className="ttl">{s.ttl}</span>
            <span className={`meta${s.fresh ? " fresh" : ""}`}>{s.meta}</span>
          </div>
        ))}
      </div>
      <Www
        rows={[
          {
            tag: "what",
            sm: "Sell premium into the event, hedged.",
            body: "A 47000/46500 put-spread sized to ₹3.2L notional, 2-day hold across the decision.",
          },
          {
            tag: "why",
            sm: "IV is rich; reversions have paid 11× before.",
            body: "Front-month IV at the 78th pct mean-reverts post-event in 11 of 11 logged BNF cases; the spread caps the tail.",
          },
          {
            tag: "how",
            sm: "Exact orders + stop, on approval.",
            body: "Routes to the proposal card below — downside acknowledged first, then you place the orders. Orff never auto-executes.",
          },
        ]}
      />
    </div>
  );
}
