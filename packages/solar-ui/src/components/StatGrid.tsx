import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface StatGridProps {
  /** Number of equal-width columns (collapses to 1 below the sm breakpoint). */
  cols?: 2 | 3 | 4;
  children?: ReactNode;
  className?: string;
}

const colsClass: Record<2 | 3 | 4, string> = {
  2: "sm:grid-cols-2",
  3: "sm:grid-cols-3",
  4: "sm:grid-cols-4",
};

/**
 * Layout convenience for composed dashboards — a responsive grid of Stat /
 * Card children so Orff never hand-builds grid markup.
 */
export function StatGrid({ cols = 2, children, className }: StatGridProps) {
  return (
    <div className={twMerge(clsx("grid grid-cols-1 gap-3", colsClass[cols], className))}>
      {children}
    </div>
  );
}
