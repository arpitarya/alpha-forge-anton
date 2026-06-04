---
id: plan-boot-llm-brokerage
domain: general
type: narrative
status: active
created: 2026-06-04
updated: 2026-06-04
---
# Plan: Add LLM + Brokerage Sync to Boot Screen

## Goal

1. **LLM gateway row** — show which AI providers are live on the boot splash.
2. **Auto-sync brokers on boot** — for any linked broker with no cached data (`_cached` is `None`), trigger `sync()` during the boot sequence and block navigation until it completes. Brokers that are `UNCONFIGURED` are skipped silently.
3. **Richer broker detail** — show holding count and sync status in the boot row once sync finishes.
4. **Verbiage polish** — footer and headline copy updates.

---

## Key facts about broker state

- `SourceStatus.UNCONFIGURED` — no credentials, never synced. Skip silently on boot.
- `SourceStatus.READY` — credentials present, `_cached` may or may not be populated (in-memory, cleared on restart). **Always needs a sync on fresh boot.**
- `SourceStatus.SYNCING` — already in flight, wait for it.
- `SourceStatus.ERROR` — last sync failed. Attempt one retry on boot; surface error if it fails again.
- `_last_synced_at` is `None` if never synced this process lifetime — the refetch loop skips these, so boot must do the first sync.
- Sync endpoint already exists: `POST /sources/{slug}/sync` (calls `src.sync()` internally).

**Implication:** on every cold boot, any broker that is not `UNCONFIGURED` needs `sync()` called. The boot screen should fire syncs concurrently (one per linked broker), animate each row through `syncing… → N holdings` or `sync failed`, and only call `onDone` when all syncs have settled.

---

## Scope

| Layer | Files touched |
|-------|--------------|
| Backend probes | `backend/app/modules/health/boot_probes.py` |
| Backend route | `backend/app/modules/health/health_routes.py` |
| Backend new endpoint | `backend/app/modules/health/health_routes.py` — `POST /health/boot/sync` |
| Frontend API | `frontend/src/modules/dashboard/boot.api.ts` |
| Frontend types | `frontend/src/modules/dashboard/boot.types.ts` |
| Frontend gate | `frontend/src/modules/dashboard/BootGate.tsx` |
| Frontend splash | `frontend/src/modules/dashboard/BootScreen.tsx` |
| Docs | `docs/architecture.md` |

---

## Step 1 — Backend: `probe_llm()` in `boot_probes.py`

Add a new async probe using `LLMGateway.health()`.

**Logic:**
- `await create_gateway().health()` → `dict[str, ProviderHealth]`
- Count available providers; pick primary from: `gemini → cerebras → groq → openrouter`
- Never raises — swallows exceptions like the other probes.

| Condition | `status` | `detail` |
|-----------|----------|----------|
| ≥1 available | `ok` | `"N providers · via <primary>"` |
| 0 available | `error` | `"no providers available"` |
| Exception | `error` | error message truncated to 48 chars |

**Label:** `"AI Gateway · LLM routing"`

---

## Step 2 — Backend: Update `probe_brokers()` in `boot_probes.py`

Enrich the `detail` field to include holding count when data is already cached:

| Status | `detail` (before) | `detail` (after) |
|--------|-------------------|------------------|
| `READY` with cache | `"linked"` | `"N holdings"` |
| `READY` no cache | `"linked"` | `"linked · not synced"` |
| `SYNCING` | `"syncing…"` | `"syncing…"` |
| `UNCONFIGURED` | `"not linked"` | `"not linked"` |
| `ERROR` | `"error"` | `"error"` |

---

## Step 3 — Backend: `POST /health/boot/sync` in `health_routes.py`

New endpoint that fires `sync()` on all non-`UNCONFIGURED` sources concurrently and returns a per-source result. Used by `BootGate` immediately after `GET /health/boot`.

```
POST /health/boot/sync
→ { results: { [slug]: { ok: bool, holdings_count: int, detail: str } } }
```

- Runs all syncs concurrently via `asyncio.gather`.
- Per-source: catches exceptions, returns `ok: false` + error detail rather than raising.
- Does not re-authenticate — if credentials are missing the source is `UNCONFIGURED` and already excluded.
- No auth dependency (same as `GET /health/boot` — boot happens before login gate).

---

## Step 4 — Frontend: `boot.types.ts`

Add `SyncResult` and `BootSyncReport` types:

```ts
export interface SyncResult {
  ok: boolean;
  holdings_count: number;
  detail: string;
}

export interface BootSyncReport {
  results: Record<string, SyncResult>;
}
```

---

## Step 5 — Frontend: `boot.api.ts`

Add `triggerBootSync()`:

```ts
export async function triggerBootSync(): Promise<BootSyncReport> {
  const res = await api.post<BootSyncReport>("/health/boot/sync");
  return res.data;
}
```

---

## Step 6 — Frontend: `BootGate.tsx` — orchestrate sync

**New flow:**

1. `GET /health/boot` → populate step list (as today).
2. `setPhase("boot")` → splash appears, animates through static rows.
3. Concurrently, fire `POST /health/boot/sync` — this is the real work.
4. When sync resolves, update the broker step `doneStatus` values with live results (`"N holdings"` or `"sync failed"`).
5. Only then allow `onDone` to fire (pass a `syncReady` flag to `BootScreen`).

**Key constraint:** the boot animation should not wait for sync before starting — it begins immediately. But `onDone` (which transitions to the app) is held until sync settles. If sync takes longer than the animation, the final row stays in a `syncing…` state until done.

---

## Step 7 — Frontend: `BootScreen.tsx`

### 7a. Static fallback `BOOT_STEPS`

Add LLM entry after `database`, before broker rows:

```ts
{ key: "llm", label: "AI Gateway · LLM routing", status: "warn", doneStatus: "no key" }
```

### 7b. `NOW_STATUS` map

```ts
llm: "connecting to AI providers…",
```

### 7c. `HEADLINES` map

```ts
llm:  "Wiring up your AI analyst…",
done: "Welcome back, Arpit.",   // already exists, no change
```

Add broker-sync headlines for linked brokers (keyed by slug):
```ts
zerodha:   "Pulling your Zerodha positions…",   // already exists
groww:     "Loading your Groww book…",           // already exists
```

### 7d. Accept `syncReady` prop

```ts
export interface BootScreenProps {
  steps?: BootStep[];
  onDone: () => void;
  exiting?: boolean;
  syncReady?: boolean;  // ← new: gate the final onDone call
}
```

The `useEffect` animation already calls `onDoneRef.current()` after the last step. Change it to: only call `onDone` if both the animation has finished **and** `syncReady === true`. If animation finishes first, wait for `syncReady` to flip; if sync finishes first, `onDone` fires as soon as animation completes.

### 7e. Footer verbiage

| Before | After |
|--------|-------|
| `N of M services online` | `N of M systems ready` |

---

## Verbiage Summary

| Location | Before | After |
|----------|--------|-------|
| Boot footer | `N of M services online` | `N of M systems ready` |
| LLM row label | _(new)_ | `AI Gateway · LLM routing` |
| LLM now-status | _(new)_ | `connecting to AI providers…` |
| LLM headline | _(new)_ | `Wiring up your AI analyst…` |
| LLM done-status (fallback) | _(new)_ | `no key` |
| LLM done-status (live, ok) | _(new)_ | `N providers · via <primary>` |
| Broker done-status (READY + cache) | `linked` | `N holdings` |
| Broker done-status (READY, just synced) | `linked` | `N holdings` |
| Broker done-status (sync failed) | `error` | `sync failed` |

---

## What does NOT change

- `BootGate` session key (`af-booted`) logic — boot still only runs once per browser session.
- Auth/login bypass — `skip` path for `/login` unchanged.
- `BootStatus` enum — `ok / warn / error / skip` covers all new states.
- Broker rows for `UNCONFIGURED` sources — still show `"not linked"` with `warn`, no sync attempted.
