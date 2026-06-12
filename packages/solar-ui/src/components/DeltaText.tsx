import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface DeltaTextProps {
  /** Signed change. Positive renders green with “+”, negative red with “−”. */
  value: number;
  /** "pct" → +1.24% · "inr" → +₹1,52,330 (en-IN grouping) · "plain" → +1.24 */
  format?: "pct" | "inr" | "plain";
  /** Trailing annotation, e.g. "TODAY". */
  suffix?: string;
  className?: string;
}

const inr = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });

function render(value: number, format: "pct" | "inr" | "plain"): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  const abs = Math.abs(value);
  if (format === "pct") return `${sign}${abs.toFixed(2)}%`;
  if (format === "inr") return `${sign}₹${inr.format(abs)}`;
  return `${sign}${abs.toLocaleString("en-IN")}`;
}

/**
 * Signed delta with red/green semantics — the recurring "+1.24%" fragment.
 * JSON-serializable props only, so Orff can compose it (ui-component-contract).
 */
export function DeltaText({ value, format = "pct", suffix, className }: DeltaTextProps) {
  const tone =
    value > 0
      ? "text-[color:var(--green)]"
      : value < 0
        ? "text-[color:var(--red)]"
        : "text-[color:var(--fg-3)]";
  return (
    <span className={twMerge(clsx("font-mono text-[11px] tabular-nums", tone, className))}>
      {render(value, format)}
      {suffix && (
        <span className="ml-1.5 text-[9px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]">
          {suffix}
        </span>
      )}
    </span>
  );
}
