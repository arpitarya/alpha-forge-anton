"use client";

import { clsx } from "clsx";

export interface PrefOption<T extends string | number> {
  value: T;
  label: string;
}

export interface PrefSegProps<T extends string | number> {
  value: T;
  options: Array<T | PrefOption<T>>;
  onChange: (v: T) => void;
}

export function PrefSeg<T extends string | number>({ value, options, onChange }: PrefSegProps<T>) {
  return (
    <div className="flex overflow-hidden rounded-[6px] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface-lo)_40%,transparent)]">
      {options.map((o) => {
        const v = (typeof o === "object" ? o.value : o) as T;
        const l = typeof o === "object" ? o.label : String(o);
        const active = v === value;
        return (
          <button
            type="button"
            key={String(v)}
            onClick={() => onChange(v)}
            className={clsx(
              "border-r border-[color:var(--line)] px-3.5 py-2 font-mono text-[10px] uppercase tracking-[0.16em] transition-colors last:border-r-0",
              active
                ? "bg-[color:color-mix(in_srgb,var(--accent)_18%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_18px_color-mix(in_srgb,var(--accent)_14%,transparent)]"
                : "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
            )}
          >
            {l}
          </button>
        );
      })}
    </div>
  );
}

export interface PrefTogProps {
  value: boolean;
  onChange: (v: boolean) => void;
}

export function PrefTog({ value, onChange }: PrefTogProps) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={value}
      onClick={() => onChange(!value)}
      className={clsx(
        "relative h-6 w-[42px] flex-shrink-0 rounded-[12px] border-none transition-colors",
        value
          ? "bg-[color:var(--accent)] shadow-[0_0_18px_var(--glow)]"
          : "bg-[color:var(--line-hi)]",
      )}
    >
      <span
        aria-hidden
        className={clsx(
          "absolute top-[3px] block h-[18px] w-[18px] rounded-full bg-white shadow-[0_1px_3px_rgba(0,0,0,0.3)] transition-transform",
          value ? "translate-x-[21px]" : "translate-x-[3px]",
        )}
      />
    </button>
  );
}

export interface PrefSliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (v: number) => void;
}

export function PrefSlider({ value, min, max, step = 1, onChange }: PrefSliderProps) {
  return (
    <div className="flex min-w-[260px] flex-1 items-center gap-3.5">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="af-pref-range h-1 flex-1 cursor-pointer appearance-none rounded-[2px] bg-[color:var(--line-hi)] outline-none"
      />
    </div>
  );
}

export interface PrefSelectProps<T extends string> {
  value: T;
  options: Array<PrefOption<T>>;
  onChange: (v: T) => void;
}

export function PrefSelect<T extends string>({ value, options, onChange }: PrefSelectProps<T>) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as T)}
      className="cursor-pointer appearance-none rounded-[6px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] px-3 py-2 pr-8 font-mono text-[11px] uppercase tracking-[0.12em] text-[color:var(--fg-2)] outline-none"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'><path fill='%23999' d='M0 0h10L5 6z'/></svg>\")",
        backgroundRepeat: "no-repeat",
        backgroundPosition: "right 12px center",
      }}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

export interface PrefInputProps {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  width?: number;
}

export function PrefInput({ value, onChange, placeholder, width = 260 }: PrefInputProps) {
  return (
    <input
      type="text"
      value={value}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
      style={{ width }}
      className="rounded-[6px] border border-[color:var(--line-hi)] bg-[color:color-mix(in_srgb,var(--surface-lo)_50%,transparent)] px-3 py-2 font-mono text-[12px] tracking-[0.04em] text-[color:var(--fg)] outline-none transition-colors focus:border-[color:var(--accent)] focus:shadow-[0_0_0_2px_color-mix(in_srgb,var(--accent)_18%,transparent)]"
    />
  );
}
