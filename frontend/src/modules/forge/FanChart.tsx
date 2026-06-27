import { FAN, fanPaths } from "./fan.utils";

/**
 * Bank-of-England-style fan chart. The P5 worst-case edge is drawn as a bold
 * red line (the figure a risk-honest system wants felt); thin data fuzzes the
 * whole band via the parent `.of-fan.low` wrapper rather than faking precision.
 * `baseline` labels today's value at the chart origin.
 */
export function FanChart({ low, baseline = "₹3.2L" }: { low?: boolean; baseline?: string }) {
  const p = fanPaths(
    low ? { rise: 70, spread: 96, skew: 1.18 } : { rise: 86, spread: 58, skew: 1.12 },
  );
  const { x0, x1, y0, W, H } = FAN;
  const a = "var(--accent)";
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Prediction fan chart: median outcome with P5–P95 band; worst case in red"
    >
      <line
        x1={x0}
        y1={y0}
        x2={x1}
        y2={y0}
        stroke="var(--line-hi)"
        strokeWidth="1"
        strokeDasharray="3 4"
      />
      <text
        x={x0 - 6}
        y={y0 + 3}
        textAnchor="end"
        fontFamily="'Space Mono',monospace"
        fontSize="8"
        fill="var(--fg-3)"
      >
        {baseline}
      </text>
      <path d={p.outer} fill={a} opacity={low ? 0.1 : 0.12} />
      <path d={p.mid} fill={a} opacity={low ? 0.12 : 0.16} />
      <path d={p.inner} fill={a} opacity={low ? 0.14 : 0.22} />
      <path
        d={p.p5}
        fill="none"
        stroke="var(--red)"
        strokeWidth="2"
        strokeDasharray={low ? "5 4" : "0"}
        opacity="0.95"
      />
      <path d={p.medLine} fill="none" stroke="var(--accent-soft)" strokeWidth="2" />
      <circle
        cx={p.xs[p.xs.length - 1]}
        cy={p.med[p.med.length - 1]}
        r="3"
        fill="var(--accent-soft)"
      />
      <text x={x0} y={H - 2} fontFamily="'Space Mono',monospace" fontSize="8" fill="var(--fg-3)">
        now
      </text>
      <text
        x={(x0 + x1) / 2}
        y={H - 2}
        textAnchor="middle"
        fontFamily="'Space Mono',monospace"
        fontSize="8"
        fill="var(--fg-3)"
      >
        +30d
      </text>
      <text
        x={x1}
        y={H - 2}
        textAnchor="end"
        fontFamily="'Space Mono',monospace"
        fontSize="8"
        fill="var(--fg-3)"
      >
        +90d
      </text>
    </svg>
  );
}
