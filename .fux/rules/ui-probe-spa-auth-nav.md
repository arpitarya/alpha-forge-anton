---
id: ui-probe-spa-auth-nav
domain: brokers
type: rule
status: active
scope: shared
created: 2026-06-28
updated: 2026-06-28
code_refs:
  - probes/ui_goals_probe.py
  - probes/ui_decisions_probe.py
  - frontend/src/modules/auth/auth.guard.tsx
  - frontend/src/modules/auth/useAuthStore.ts
  - probes/Probes.md
related:
  - probe-cdp-not-playwright
---
**Rule:** A CDP probe for an **authed SPA page** must not reach it with a full
`page.goto('/<page>')`. Seed auth into storage in an **init script** (runs before any
app script), `goto('/')` and let the auth store rehydrate, then **client-navigate via
the in-app nav button** (`get_by_role("button", name="<Tab>")` → click →
`wait_for_url`). The hydrated store stays in memory across the SPA transition.

**Why:** `useAuthStore` is `zustand/persist`, which **rehydrates asynchronously** —
after the first render. `AuthGuard` runs its effect with `accessToken === null` on a
fresh full-page load and `router.replace('/login')` *before* rehydration lands, so a
direct `goto('/goals')` bounces `/goals → /login → /` and every selector times out.
Landing on `/` first lets the store rehydrate once; a client-side nav then never
remounts the store, so the guard sees the token. Setting `localStorage` *after*
`goto` (the old pattern) doesn't help — rehydration timing, not storage presence, is
the race. This silently broke **all** UI probes after the iam-session/boot-screen
changes; it surfaced only when a probe finally got past navigation.

**Edge cases:**
- The visible nav items are **buttons** calling `router.push`, not `<a>` — match by
  button role/name, not a link href (an `<a href="/goals">` honeypot exists offscreen).
- Chips/labels are UPPERCASED via CSS `text-transform`; `innerText` reflects it, so
  text assertions must be case-insensitive.
- Mock the SSE endpoints (`boot/sync-stream`, `concierge`); never wait `networkidle`
  on a page holding an open stream — it never settles. Use `domcontentloaded` + explicit waits.
