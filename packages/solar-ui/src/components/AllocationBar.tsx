import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface AllocationSegment {
  label: string;
  /** Share in percent (0–100). Segments are rendered in order, left to right. */
  pct: number;
}

export interface AllocationBarProps {
  segments: AllocationSegment[];
  /** Render a label · pct legend beneath the bar. */
  showLegend?: boolean;
  height?: number;
  className?: string;
}

export const CHART_PALETTE = [
  "var(--accent)",
  "var(--color-af-green)",
  "var(--color-af-orange)",
  "var(--color-af-purple)",
  "var(--color-af-blue)",
  "var(--color-af-red)",
];

/**
 * Stacked horizontal allocation bar — the natural rendering of a target mix or
 * plan drift. JSON-serializable props only (ui-component-contract).
 */
export function AllocationBar({
  segments,
  showLegend = true,
  height = 10,
  className,
}: AllocationBarProps) {
  if (!segments.length) return null;
  return (
    <div className={twMerge(clsx("w-full", className))}>
      <div
        className="flex w-full overflow-hidden rounded-full border border-[color:var(--line)]"
        style={{ height }}
      >
        {segments.map((s, i) => (
          <div
            key={s.label}
            title={`${s.label} ${s.pct.toFixed(1)}%`}
            style={{
              width: `${Math.max(s.pct, 0)}%`,
              background: CHART_PALETTE[i % CHART_PALETTE.length],
              opacity: 0.85,
            }}
          />
        ))}
      </div>
      {showLegend && (
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
          {segments.map((s, i) => (
            <span
              key={s.label}
              className="flex items-center gap-1.5 font-mono text-[10px] text-[color:var(--fg-3)]"
            >
              <span
                aria-hidden
                className="inline-block h-2 w-2 rounded-sm"
                style={{ background: CHART_PALETTE[i % CHART_PALETTE.length] }}
              />
              {s.label}
              <span className="text-[color:var(--fg-2)] tabular-nums">{s.pct.toFixed(1)}%</span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
