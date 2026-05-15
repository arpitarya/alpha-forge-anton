"use client";

import { clsx } from "clsx";
import { useEffect, useRef } from "react";

export interface SearchBoxProps {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

export function SearchBox({ value, onChange, placeholder }: SearchBoxProps) {
  const ref = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handle(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement | null)?.tagName;
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "f") {
        e.preventDefault();
        ref.current?.focus();
      } else if (e.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA") {
        e.preventDefault();
        ref.current?.focus();
      }
    }
    document.addEventListener("keydown", handle);
    return () => document.removeEventListener("keydown", handle);
  }, []);

  const hasQ = !!value;
  return (
    <div className={clsx("relative flex w-[240px] flex-shrink-0 items-center")}>
      <svg
        viewBox="0 0 24 24"
        role="img"
        aria-label="Search"
        className={clsx(
          "pointer-events-none absolute left-[9px] h-[13px] w-[13px] transition-colors",
          hasQ ? "text-[color:var(--accent)]" : "text-[color:var(--fg-3)]",
        )}
      >
        <title>Search</title>
        <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
        <path d="M21 21l-4.3-4.3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <input
        ref={ref}
        type="text"
        value={value}
        placeholder={placeholder ?? "Search symbols, sectors, regions…"}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-[6px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] py-2 pl-[30px] pr-[36px] font-mono text-[11px] tracking-[0.04em] text-[color:var(--fg)] outline-none transition placeholder:text-[color:var(--fg-3)] focus:border-[color:var(--accent)] focus:bg-[color:color-mix(in_srgb,var(--surface-lo)_80%,transparent)] focus:shadow-[0_0_0_2px_color-mix(in_srgb,var(--accent)_18%,transparent)]"
      />
      {!hasQ && (
        <span className="pointer-events-none absolute right-[9px] flex h-[15px] items-center rounded-[3px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface)_60%,transparent)] px-[5px] font-mono text-[10px] text-[color:var(--fg-3)]">
          /
        </span>
      )}
      {hasQ && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="absolute right-[6px] grid h-[18px] w-[18px] place-items-center rounded-[3px] text-[color:var(--fg-3)] hover:bg-[color:color-mix(in_srgb,var(--accent)_12%,transparent)] hover:text-[color:var(--accent)]"
        >
          <svg viewBox="0 0 24 24" width="12" height="12" role="img" aria-label="Clear">
            <title>Clear</title>
            <path
              d="M6 6l12 12M18 6l-12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
