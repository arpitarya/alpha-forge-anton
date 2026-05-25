"use client"

import { PrefGroup, PrefRow } from "@alphaforge-anton/solar-ui"
import { useRouter } from "next/navigation"

import { useExtendSession, useRevokeSession, useSessions } from "@/modules/auth/auth.query"
import { useAuthStore } from "@/modules/auth/useAuthStore"

function fmt(iso: string) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" })
}

function device(hint: string | null) {
  if (!hint) return "Unknown device"
  if (/mobile|android|iphone/i.test(hint)) return "Mobile"
  if (/curl|python|httpx/i.test(hint)) return "Script"
  return "Browser"
}

export function SessionsGroup() {
  const router = useRouter()
  const { data: sessions, isLoading } = useSessions()
  const extend = useExtendSession()
  const revoke = useRevokeSession()
  const logout = useAuthStore((s) => s.logout)

  async function handleLogout() {
    await logout()
    router.replace("/login")
  }

  return (
    <PrefGroup num="04" title="Sessions" meta={sessions ? `${sessions.length} active` : undefined}>
      <PrefRow
        name="Sign out this device"
        desc="Revokes the current session. Other devices stay logged in."
        control={<SignOutBtn onClick={handleLogout}>Sign out</SignOutBtn>}
      />
      {isLoading && (
        <p className="py-3 font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
          Loading sessions…
        </p>
      )}
      {sessions?.map((s) => (
        <div
          key={s.id}
          className="flex items-start justify-between gap-3 border-b border-[color:var(--line)] py-3 last:border-b-0"
        >
          <div className="min-w-0">
            <div className="text-[13px] font-medium">{device(s.device_hint)}</div>
            <div className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.12em] text-[color:var(--fg-3)]">
              {s.ip_address ?? "—"} · last active {fmt(s.last_active_at)}
            </div>
            <div className="mt-0.5 font-mono text-[10px] tracking-[0.08em] text-[color:var(--fg-4)]">
              idle expires {fmt(s.idle_expires_at)}
            </div>
          </div>
          <div className="flex flex-shrink-0 gap-2">
            <ActionBtn
              onClick={() => extend.mutate({ id: s.id })}
              disabled={extend.isPending}
            >
              Extend
            </ActionBtn>
            <SignOutBtn
              onClick={() => revoke.mutate(s.id)}
              disabled={revoke.isPending}
            >
              Revoke
            </SignOutBtn>
          </div>
        </div>
      ))}
    </PrefGroup>
  )
}

function ActionBtn(p: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      {...p}
      className="rounded-[5px] border border-[color:var(--line-hi)] px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--fg-2)] transition hover:border-[color:var(--fg-3)] hover:text-[color:var(--fg)] disabled:cursor-default disabled:opacity-40"
    />
  )
}

function SignOutBtn(p: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      {...p}
      className="rounded-[6px] border border-[color:color-mix(in_srgb,var(--red)_50%,transparent)] bg-[color:color-mix(in_srgb,var(--red)_8%,transparent)] px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[color:var(--red)] transition hover:bg-[color:color-mix(in_srgb,var(--red)_16%,transparent)] disabled:cursor-default disabled:opacity-40"
    />
  )
}
