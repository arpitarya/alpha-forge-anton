import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface TopBarNavItem {
  id: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export interface TopBarProps {
  brand?: ReactNode;
  nav?: TopBarNavItem[];
  /** Right-side cluster — status pills, kbd hints, user chip. */
  right?: ReactNode;
  className?: string;
}

/**
 * Hi-Fi `.top` — slim global header. Padding/sizes track the Hi-Fi spec:
 * 4px 14px outer, 32px min-height, 8px radius, nav buttons 4px 10px @ 9px font.
 *
 * Auto-hide: when an ancestor carries `chrome-autohide`, the bar collapses to
 * a thin accent strip and expands on hover/focus.
 */
export function TopBar({ brand, nav, right, className }: TopBarProps) {
  return (
    <header
      data-af-top
      className={twMerge(
        clsx(
          "af-top group/top relative flex min-h-[32px] flex-none items-center justify-between gap-3.5",
          "rounded-[8px] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_78%,transparent)]",
          "px-3.5 py-1 [backdrop-filter:blur(20px)] [-webkit-backdrop-filter:blur(20px)]",
          "after:absolute after:inset-x-6 after:-bottom-px after:h-px",
          "after:bg-[linear-gradient(90deg,transparent,color-mix(in_srgb,var(--accent)_45%,transparent),transparent)]",
          "after:opacity-35 after:content-['']",
          className,
        ),
      )}
    >
      {brand && <div className="flex items-center gap-2.5">{brand}</div>}
      {nav && nav.length > 0 && (
        <nav className="flex items-center gap-0.5">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              disabled={item.disabled}
              onClick={item.onClick}
              className={clsx(
                "relative inline-flex items-center justify-center rounded-[5px]",
                "px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.22em] transition-colors",
                item.active
                  ? "text-[color:var(--accent)]"
                  : "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
                item.disabled && "opacity-50 cursor-not-allowed",
                item.active &&
                  "after:absolute after:left-1/2 after:-bottom-0.5 after:h-[1.5px] after:w-[18px] after:-translate-x-1/2 after:rounded-[1px] after:bg-[color:var(--accent)] after:shadow-[0_0_8px_var(--glow)] after:content-['']",
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>
      )}
      {right && (
        <div className="flex items-center gap-2 font-mono text-[9.5px] text-[color:var(--fg-3)]">
          {right}
        </div>
      )}
    </header>
  );
}
