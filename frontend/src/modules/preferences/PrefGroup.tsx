import type { ReactNode } from "react";

export interface PrefGroupProps {
  num?: string;
  title: string;
  meta?: string;
  children: ReactNode;
}

export function PrefGroup({ num, title, meta, children }: PrefGroupProps) {
  return (
    <section
      className="relative rounded-[10px] border border-[color:var(--line)] px-6 py-5"
      style={{ background: "color-mix(in srgb, var(--surface) 88%, transparent)" }}
    >
      <span
        aria-hidden
        className="pointer-events-none absolute left-0 top-0 h-px w-8 opacity-50"
        style={{ background: "linear-gradient(90deg, var(--accent), transparent)" }}
      />
      <header className="mb-3.5 flex items-center justify-between border-b border-[color:var(--line)] pb-3">
        <div className="flex items-baseline gap-2.5 text-[14px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">
          {num && (
            <span className="font-mono text-[10px] tracking-[0.22em] text-[color:var(--accent)]">{num}</span>
          )}
          <span>{title}</span>
        </div>
        {meta && (
          <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
            {meta}
          </span>
        )}
      </header>
      {children}
    </section>
  );
}
