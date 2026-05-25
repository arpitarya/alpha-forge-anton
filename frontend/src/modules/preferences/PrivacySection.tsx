"use client";

import { PrefGroup, PrefRow, PrefSelect, PrefTog } from "@alphaforge-anton/solar-ui";
import { useRouter } from "next/navigation";
import { logoutAll } from "@/modules/auth/auth.api";
import { useAuthStore } from "@/modules/auth/useAuthStore";
import type { PrefDraft } from "./usePrefStore";

export interface PrivacySectionProps {
  t: PrefDraft;
  setTweak: <K extends keyof PrefDraft>(k: K, v: PrefDraft[K]) => void;
}

export function PrivacySection({ t, setTweak }: PrivacySectionProps) {
  const router = useRouter();
  const clearAuth = useAuthStore((s) => s.clearAuth);

  async function handleLogoutAll() {
    try { await logoutAll() } catch { /* best-effort */ }
    clearAuth();
    router.replace("/login");
  }

  return (
    <>
      <PrefGroup num="01" title="Telemetry">
        <PrefRow
          name="Anonymous usage analytics"
          desc="Helps us tune which screens are slow. No order data or holdings are ever sent."
          control={<PrefTog value={t.telemetry} onChange={(v) => setTweak("telemetry", v)} />}
          tail={t.telemetry ? "On" : "Off"}
        />
        <PrefRow
          name="Crash reports"
          desc="Send stack traces when the terminal crashes."
          control={<PrefTog value={t.crashReports} onChange={(v) => setTweak("crashReports", v)} />}
          tail={t.crashReports ? "On" : "Off"}
        />
        <PrefRow
          name="Share trades with Alpha for training"
          desc="Off by default. Your fills never leave the local DB unless you turn this on."
          control={<PrefTog value={t.shareTrades} onChange={(v) => setTweak("shareTrades", v)} />}
          tail={t.shareTrades ? "Shared" : "Local only"}
        />
      </PrefGroup>

      <PrefGroup num="02" title="Data">
        <PrefRow
          name="Local history retention"
          desc="How long to keep tick history and chat transcripts on this machine."
          control={
            <PrefSelect
              value={t.retention}
              options={[
                { value: "30", label: "30 days" },
                { value: "90", label: "90 days" },
                { value: "365", label: "1 year" },
                { value: "all", label: "Forever" },
              ]}
              onChange={(v) => setTweak("retention", v)}
            />
          }
        />
        <PrefRow
          name="Clear cache"
          desc="Wipes local screener features, sparkline buffers, and ticker history."
          control={<DangerButton>Clear local cache</DangerButton>}
        />
        <PrefRow
          name="Sign out everywhere"
          desc="Revokes all sessions and signs you out of every device."
          control={<DangerButton onClick={handleLogoutAll}>Sign out all sessions</DangerButton>}
        />
      </PrefGroup>
    </>
  );
}

function DangerButton(p: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      {...p}
      className="rounded-[6px] border border-[color:color-mix(in_srgb,var(--red)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--red)_8%,transparent)] px-4 py-2 font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--red)] transition hover:bg-[color:color-mix(in_srgb,var(--red)_16%,transparent)] hover:shadow-[0_0_18px_color-mix(in_srgb,var(--red)_24%,transparent)]"
    />
  );
}
