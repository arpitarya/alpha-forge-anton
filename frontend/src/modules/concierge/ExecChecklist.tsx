import { EXEC_ORDERS } from "./proposal.mock";

/** Post-approve execution checklist — the exact orders YOU place. Orff never
 * auto-executes; the card is honest about where the human takes over. */
export function ExecChecklist() {
  return (
    <div className="of-exec">
      <div className="of-sub">Execution checklist · you place these</div>
      {EXEC_ORDERS.map((o, i) => (
        <div className="of-order" key={o.ord}>
          <span className="ix">{i + 1}</span>
          <span className="ord">{o.ord}</span>
          <span
            className="side"
            style={o.side === "guard" ? { color: "var(--accent)" } : undefined}
          >
            {o.side}
          </span>
        </div>
      ))}
      <div className="noauto">⚠ Orff never auto-executes — copy to broker to place</div>
    </div>
  );
}
