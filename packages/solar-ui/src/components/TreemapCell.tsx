import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface TreemapCellProps {
  symbol: string;
  sublabel?: string;
  value: ReactNode;
  change: ReactNode;
  /** -100..100 — drives bg tint (negative = red, positive = green). */
  pnlPct: number;
  /** Render larger sym font. */
  big?: boolean;
  /** Optional decorative right-corner element (e.g. a <Sparkline />). */
  decoration?: ReactNode;
  /** Absolute-positioning style props (left/top/width/height). */
  style?: React.CSSProperties;
  onClick?: () => void;
  className?: string;
}

// Pixel-area thresholds for progressive disclosure
const AREA_MICRO = 3000;   // only tint, no text
const AREA_TINY  = 7000;   // symbol only, no sublabel/value
const AREA_SMALL = 18000;  // symbol + change%, no sublabel

/**
 * Hi-Fi `.tm-cell`. Designed to be absolutely positioned by a parent treemap
 * layout — pass `style={{ left, top, width, height }}`. Tint scales with
 * `pnlPct`: stronger sign → more saturated bg (color-mix with --green/--red).
 */
export function TreemapCell({
  symbol,
  sublabel,
  value,
  change,
  pnlPct,
  big = false,
  decoration,
  style,
  onClick,
  className,
}: TreemapCellProps) {
  const w = (style as { width?: number })?.width ?? 0;
  const h = (style as { height?: number })?.height ?? 0;
  const area = w * h;

  const isMicro = area < AREA_MICRO;
  const isTiny  = area < AREA_TINY;
  const isSmall = area < AREA_SMALL;

  // Map |pnlPct| to a 4..38% tint mix — stronger signal at extremes.
  const intensity = Math.min(38, 4 + Math.abs(pnlPct) * 4);
  const tone = pnlPct >= 0 ? "var(--green)" : "var(--red)";
  const bg = `color-mix(in srgb, ${tone} ${intensity}%, var(--surface))`;
  const isInteractive = !!onClick;

  const pad = isTiny ? "p-1.5" : isSmall ? "p-2.5" : "p-3";

  return (
    <div
      onClick={onClick}
      onKeyDown={
        isInteractive
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onClick?.();
            }
          : undefined
      }
      role={isInteractive ? "button" : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      style={{ ...style, background: bg }}
      className={twMerge(
        clsx(
          "absolute flex flex-col justify-between overflow-hidden rounded-[3px]",
          "border border-[color:var(--line-hi)] border-opacity-40",
          "transition-transform duration-200 hover:scale-[1.015] hover:z-10",
          "hover:shadow-[0_0_28px_color-mix(in_srgb,var(--accent)_20%,transparent)]",
          pad,
          isInteractive && "cursor-pointer",
          className,
        ),
      )}
    >
      {!isMicro && (
        <>
          <div className="relative min-h-0">
            <div
              className={clsx(
                "truncate font-semibold leading-tight text-[color:var(--fg)]",
                big ? "text-[18px]" : isTiny ? "text-[9px]" : isSmall ? "text-[11px]" : "text-[13px]",
              )}
            >
              {symbol}
            </div>
            {!isTiny && !isSmall && sublabel && (
              <div className="truncate font-mono text-[9px] uppercase tracking-[0.14em] text-[color:var(--fg-3)] opacity-70">
                {sublabel}
              </div>
            )}
          </div>
          {decoration && (
            <div className="absolute right-1.5 top-1.5 opacity-40">{decoration}</div>
          )}
          {!isTiny && (
            <div className="flex items-end justify-between gap-1 min-h-0">
              {!isSmall && (
                <div className="truncate font-mono text-[11px] tabular-nums text-[color:var(--fg)] opacity-80">
                  {value}
                </div>
              )}
              <div
                className={clsx(
                  "font-mono tabular-nums ml-auto",
                  isSmall ? "text-[9px]" : "text-[10px]",
                  pnlPct >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]",
                )}
              >
                {change}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
