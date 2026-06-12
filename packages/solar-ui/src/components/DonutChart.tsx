import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { CHART_PALETTE } from "./AllocationBar";

export interface DonutSlice {
  label: string;
  /** Absolute or percentage value — slices are normalized to the total. */
  value: number;
}

export interface DonutChartProps {
  slices: DonutSlice[];
  size?: number;
  thickness?: number;
  /** Center caption, e.g. "6 classes". */
  caption?: string;
  showLegend?: boolean;
  className?: string;
}

/**
 * SVG donut for allocation splits — pairs with percentages-only payloads from
 * /plans/drift or holdings buckets. JSON-serializable props only.
 */
export function DonutChart({
  slices,
  size = 140,
  thickness = 16,
  caption,
  showLegend = true,
  className,
}: DonutChartProps) {
  const total = slices.reduce((acc, s) => acc + Math.max(s.value, 0), 0);
  if (!total) return null;
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  let offset = 0;

  return (
    <div className={twMerge(clsx("flex items-center gap-4", className))}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-hidden>
        <title>{caption ?? "allocation"}</title>
        {slices.map((s, i) => {
          const frac = Math.max(s.value, 0) / total;
          const dash = `${frac * c} ${c}`;
          const el = (
            <circle
              key={s.label}
              cx={size / 2}
              cy={size / 2}
              r={r}
              fill="none"
              stroke={CHART_PALETTE[i % CHART_PALETTE.length]}
              strokeWidth={thickness}
              strokeDasharray={dash}
              strokeDashoffset={-offset * c}
              opacity={0.85}
              transform={`rotate(-90 ${size / 2} ${size / 2})`}
            />
          );
          offset += frac;
          return el;
        })}
        {caption && (
          <text
            x="50%"
            y="50%"
            dominantBaseline="middle"
            textAnchor="middle"
            className="fill-[color:var(--fg-3)] font-mono text-[10px]"
          >
            {caption}
          </text>
        )}
      </svg>
      {showLegend && (
        <div className="flex flex-col gap-1">
          {slices.map((s, i) => (
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
              <span className="text-[color:var(--fg-2)] tabular-nums">
                {((s.value / total) * 100).toFixed(1)}%
              </span>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
