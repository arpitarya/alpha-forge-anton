import { clsx } from "clsx";
import { useId } from "react";
import { twMerge } from "tailwind-merge";

export interface LineChartProps {
  /** y-values, evenly spaced. */
  series: number[];
  /** x labels — first and last are rendered (e.g. ["2026", "2036"]). */
  labels?: string[];
  /** Optional confidence band (projections): per-point low/high envelopes. */
  bandLo?: number[];
  bandHi?: number[];
  width?: number;
  height?: number;
  tone?: "up" | "dn" | "accent" | "neutral";
  /** Format min/max axis labels: "inr" → ₹12,40,000. */
  yFormat?: "inr" | "plain";
  className?: string;
}

const toneColor = {
  up: "var(--green)",
  dn: "var(--red)",
  accent: "var(--accent)",
  neutral: "var(--fg-3)",
};
const inr = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
const fmt = (v: number, f: "inr" | "plain") => (f === "inr" ? `₹${inr.format(v)}` : `${v}`);

/**
 * Axis-annotated SVG line chart with an optional projection band — Sparkline's
 * bigger sibling for history and forward projections. Serializable props only.
 */
export function LineChart({
  series,
  labels,
  bandLo,
  bandHi,
  width = 420,
  height = 140,
  tone = "accent",
  yFormat = "plain",
  className,
}: LineChartProps) {
  const id = useId();
  if (series.length < 2) return null;
  const all = [...series, ...(bandLo ?? []), ...(bandHi ?? [])];
  const min = Math.min(...all);
  const max = Math.max(...all);
  const range = max - min || 1;
  const pad = 4;
  const x = (i: number, n: number) => pad + (i * (width - 2 * pad)) / (n - 1);
  const y = (v: number) => height - pad - ((v - min) / range) * (height - 2 * pad);
  const path = (pts: number[]) =>
    pts.map((v, i) => `${i === 0 ? "M" : "L"}${x(i, pts.length).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const band =
    bandLo && bandHi && bandLo.length === series.length && bandHi.length === series.length
      ? `${path(bandHi)} ${bandLo
          .map((v, i, a) => `L${x(a.length - 1 - i, a.length).toFixed(1)},${y(a[a.length - 1 - i]).toFixed(1)}`)
          .join(" ")} Z`
      : null;
  const color = toneColor[tone];

  return (
    <div className={twMerge(clsx("font-mono text-[9px] text-[color:var(--fg-3)]", className))}>
      <div className="flex justify-between tabular-nums">
        <span>{fmt(max, yFormat)}</span>
        {labels && labels.length > 1 && <span>{labels[labels.length - 1]}</span>}
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" role="img" aria-hidden>
        {band && (
          <>
            <defs>
              <linearGradient id={`lc-${id}`} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity="0.25" />
                <stop offset="100%" stopColor={color} stopOpacity="0.04" />
              </linearGradient>
            </defs>
            <path d={band} fill={`url(#lc-${id})`} />
          </>
        )}
        <path d={path(series)} fill="none" stroke={color} strokeWidth={1.6} />
      </svg>
      <div className="flex justify-between tabular-nums">
        <span>{fmt(min, yFormat)}</span>
        {labels && labels.length > 0 && <span>{labels[0]}</span>}
      </div>
    </div>
  );
}
