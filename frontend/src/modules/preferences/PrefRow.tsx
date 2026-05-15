import type { ReactNode } from "react";

export interface PrefRowProps {
  name: string;
  desc?: string;
  control: ReactNode;
  tail?: ReactNode;
}

export function PrefRow({ name, desc, control, tail }: PrefRowProps) {
  return (
    <div
      className="grid items-center gap-[18px] border-b border-[color:var(--line)] py-3.5 last:border-b-0 last:pb-0"
      style={{ gridTemplateColumns: "200px 1fr auto" }}
    >
      <div className="flex min-w-0 flex-col gap-1">
        <span className="text-[13px] font-medium tracking-[-0.005em] text-[color:var(--fg)]">{name}</span>
        {desc && (
          <span className="font-mono text-[10px] leading-[1.55] tracking-[0.04em] text-[color:var(--fg-3)]">
            {desc}
          </span>
        )}
      </div>
      <div className="flex min-w-0 flex-wrap items-center gap-3">{control}</div>
      <div className="min-w-[80px] text-right font-mono text-[10px] uppercase tracking-[0.16em] text-[color:var(--fg-3)] tabular-nums">
        {tail}
      </div>
    </div>
  );
}
