import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface DiffRow {
  /** Row label, e.g. an asset class or holding. */
  label: string;
  /** Current value, pre-formatted upstream (e.g. "55%", "₹4.2L"). */
  before: string | number;
  /** Proposed value, pre-formatted upstream. */
  after: string | number;
  /** Optional signed annotation, e.g. "+5pts" or "−₹40k". */
  delta?: string;
  /** Drives the row tone: "add" green, "remove" red, else neutral. */
  kind?: "add" | "remove" | "same";
}

export interface DiffTableProps {
  rows: DiffRow[];
  beforeLabel?: string;
  afterLabel?: string;
  maxRows?: number;
  className?: string;
}

const TONE: Record<string, string> = {
  add: "text-[color:var(--green)]",
  remove: "text-[color:var(--red)]",
  same: "text-[color:var(--fg-2)]",
};

/**
 * Before/after comparison for a proposed plan change — a rebalance or
 * reallocation rendered as a two-column diff rather than a prose paragraph.
 * Declarative rows, no callbacks — JSON-composable (ui-component-contract).
 */
export function DiffTable({
  rows,
  beforeLabel = "Now",
  afterLabel = "Proposed",
  maxRows = 12,
  className,
}: DiffTableProps) {
  if (!rows.length) return null;
  const visible = rows.slice(0, maxRows);
  return (
    <table className={twMerge(clsx("w-full border-collapse text-[12px]", className))}>
      <thead>
        <tr>
          {["", beforeLabel, afterLabel, ""].map((h, i) => (
            <th
              // biome-ignore lint/suspicious/noArrayIndexKey: static header cells
              key={i}
              className={clsx(
                "border-b border-[color:var(--line)] px-2 py-1.5 font-mono text-[9px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]",
                i === 0 ? "text-left" : "text-right",
              )}
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {visible.map((row, ri) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: rows are static spec data
          <tr key={ri}>
            <td className="border-b border-[color:color-mix(in_srgb,var(--line)_50%,transparent)] px-2 py-1.5 text-left text-[color:var(--fg-2)]">
              {row.label}
            </td>
            <td className="border-b border-[color:color-mix(in_srgb,var(--line)_50%,transparent)] px-2 py-1.5 text-right tabular-nums text-[color:var(--fg-3)] line-through decoration-[color:var(--fg-4)]">
              {row.before}
            </td>
            <td
              className={clsx(
                "border-b border-[color:color-mix(in_srgb,var(--line)_50%,transparent)] px-2 py-1.5 text-right font-medium tabular-nums",
                TONE[row.kind ?? "same"],
              )}
            >
              {row.after}
            </td>
            <td
              className={clsx(
                "border-b border-[color:color-mix(in_srgb,var(--line)_50%,transparent)] px-2 py-1.5 text-right font-mono text-[10px] tabular-nums",
                TONE[row.kind ?? "same"],
              )}
            >
              {row.delta ?? ""}
            </td>
          </tr>
        ))}
      </tbody>
      {rows.length > maxRows && (
        <caption className="caption-bottom pt-1 text-right font-mono text-[9px] text-[color:var(--fg-3)]">
          +{rows.length - maxRows} more
        </caption>
      )}
    </table>
  );
}
