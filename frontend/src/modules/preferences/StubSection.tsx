import { PrefGroup } from "@alphaforge-anton/solar-ui";

export interface StubSectionProps {
  label: string;
}

export function StubSection({ label }: StubSectionProps) {
  return (
    <PrefGroup num="—" title={label} meta="Coming soon">
      <p className="font-mono text-[11px] leading-[1.7] tracking-[0.04em] text-[color:var(--fg-3)]">
        {label} settings will live here. Wired controls land alongside the matching backend
        endpoints — see the AlphaForge Anton Hi-Fi spec for the planned rows.
      </p>
    </PrefGroup>
  );
}
