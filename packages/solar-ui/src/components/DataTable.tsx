import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface DataTableColumn {
  /** Row-object key to read. */
  key: string;
  label: string;
  align?: "left" | "right";
}

export interface DataTableProps {
  columns: DataTableColumn[];
  /** Cell values are plain strings/numbers — already formatted upstream. */
  rows: Record<string, string | number>[];
  /** Cap rendered rows (composed tables stay glanceable). */
  maxRows?: number;
  className?: string;
}

/**
 * Compact data table for composed holdings / screener / drift rows.
 * Declarative columns + rows, no callbacks — JSON-composable by construction.
 */
export function DataTable({ columns, rows, maxRows = 12, className }: DataTableProps) {
  if (!columns.length || !rows.length) return null;
  const visible = rows.slice(0, maxRows);
  return (
    <table className={twMerge(clsx("w-full border-collapse text-[12px]", className))}>
      <thead>
        <tr>
          {columns.map((c) => (
            <th
              key={c.key}
              className={clsx(
                "border-b border-[color:var(--line)] px-2 py-1.5 font-mono text-[9px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]",
                c.align === "right" ? "text-right" : "text-left",
              )}
            >
              {c.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {visible.map((row, ri) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: rows are static spec data
          <tr key={ri}>
            {columns.map((c) => (
              <td
                key={c.key}
                className={clsx(
                  "border-b border-[color:color-mix(in_srgb,var(--line)_50%,transparent)] px-2 py-1.5 text-[color:var(--fg-2)] tabular-nums",
                  c.align === "right" ? "text-right" : "text-left",
                )}
              >
                {row[c.key] ?? "—"}
              </td>
            ))}
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
