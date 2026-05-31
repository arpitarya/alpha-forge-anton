"use client";

import { notify } from "@alphaforge-anton/solar-ui";
import { type QueryClient, useQueryClient } from "@tanstack/react-query";
import { usePathname } from "next/navigation";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { BootScreen, type BootStep } from "./BootScreen";
import { fetchBootReport, streamBootSync } from "./boot.api";
import { diagnose } from "./boot.diagnose";
import type { BootService, SyncResult } from "./boot.types";

const SYNC_TOAST_ID = "boot-sync";
const POLL_MS = 2000;

const GATE_ENABLED =
  (process.env.NEXT_PUBLIC_BOOT_GATE_ENABLED ?? "true").toLowerCase() !== "false";

// A service is "blocking" the boot page when its state means the terminal
// can't safely render. Only ERROR halts — vault locked, db down, llm dead.
// WARN is reserved for non-critical states (vault token absent → file env,
// broker not linked → intentional). Vault-locked already returns ERROR from
// probe_vault, so the simple "error blocks" rule covers the unlock flow.
function isBlocking(s: BootService): boolean {
  return s.status === "error";
}

// A row is "cached" if it's healthy and needs no work at boot. Errors must be
// retried; brokers stuck at "linked · not synced"/"syncing…" must be primed
// before holdings render. "not linked" is intentional config absence — cached.
function isCached(s: BootService): boolean {
  if (s.status === "error") return false;
  if (s.detail === "linked · not synced") return false;
  if (s.detail === "syncing…") return false;
  return true;
}

// Only broker rows are emitted by /health/boot/sync-stream, so they're the
// only ones we can drive progress from when running the broker sync.
function isBrokerRow(s: BootService): boolean {
  return s.label.includes("holdings source");
}

function toStep(s: BootService): BootStep {
  return { key: s.key, label: s.label, status: s.status, doneStatus: s.detail || "—" };
}

function emitProgress(done: number, total: number, errors: number): void {
  const totalLabel = total > 0 ? `${done} / ${total}` : `${done} done`;
  notify.sync({
    id: SYNC_TOAST_ID,
    title: "Syncing brokers",
    pill: errors > 0 ? `${errors} failed` : totalLabel,
    message:
      total > 0
        ? `Fetching holdings from your connected brokers · ${totalLabel}`
        : "Fetching holdings from your connected brokers.",
  });
}

function runSync(signal: AbortSignal, totalGuess: number, qc: QueryClient): Promise<void> {
  const results: Array<SyncResult & { slug: string }> = [];
  emitProgress(0, totalGuess, 0);

  return streamBootSync((slug, res) => {
    results.push({ slug, ...res });
    const errors = results.filter((r) => !r.ok).length;
    emitProgress(results.length, Math.max(totalGuess, results.length), errors);
  }, signal)
    .catch(() => {
      /* abort or transport error — fall through to summary */
    })
    .finally(() => {
      const failures = results.filter((r) => !r.ok);
      const synced = results.filter((r) => r.ok && r.detail.includes("holdings"));
      if (synced.length > 0) {
        qc.invalidateQueries({ queryKey: ["portfolio"] });
      }
      announce(failures, synced.length, results.length);
    });
}

type AnnounceFailure = { slug: string; reason?: string; detail: string };

function announce(failures: AnnounceFailure[], syncedCount: number, total: number): void {
  if (total === 0) {
    notify.dismiss(SYNC_TOAST_ID);
    return;
  }
  if (failures.length > 0) {
    const dx = diagnose(failures, total);
    notify.error({
      id: SYNC_TOAST_ID,
      title: dx.title,
      pill: `${failures.length}/${total}`,
      message: dx.message,
      actions: dx.actions,
    });
    return;
  }
  if (syncedCount > 0) {
    notify.ok({
      id: SYNC_TOAST_ID,
      title: `${syncedCount} broker${syncedCount === 1 ? "" : "s"} synced`,
      pill: "ready",
      ttl: 3500,
    });
  } else {
    notify.dismiss(SYNC_TOAST_ID);
  }
}

// Legacy code path: when NEXT_PUBLIC_BOOT_GATE_ENABLED=false, fall back to the
// old background-probe behaviour with no blocking splash. Kept for screenshots
// and dev iteration where waiting on vault unlock is friction.
function useBackgroundBoot(skip: boolean, qc: QueryClient): void {
  useEffect(() => {
    if (skip) return;
    const ctrl = new AbortController();
    fetchBootReport()
      .then((r) => {
        const needs = r.services.filter((s) => !isCached(s));
        if (needs.length === 0) {
          qc.invalidateQueries({ queryKey: ["portfolio"] });
          return;
        }
        const brokerNeeds = needs.filter(isBrokerRow);
        runSync(ctrl.signal, brokerNeeds.length, qc);
      })
      .catch(() => runSync(ctrl.signal, 0, qc));
    return () => ctrl.abort();
  }, [skip, qc]);
}

export function BootGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const qc = useQueryClient();
  const skipBoot = pathname === "/login";

  const gateActive = GATE_ENABLED && !skipBoot;

  // Background mode (gate disabled) — preserve the prior behaviour so dev
  // workflows that don't run the vault keep working.
  useBackgroundBoot(skipBoot || GATE_ENABLED, qc);

  if (!gateActive) return <>{children}</>;
  return <BlockingBoot qc={qc}>{children}</BlockingBoot>;
}

function BlockingBoot({ children, qc }: { children: ReactNode; qc: QueryClient }) {
  const [services, setServices] = useState<BootService[] | null>(null);
  const [synced, setSynced] = useState(false);
  const [exited, setExited] = useState(false);
  const [exiting, setExiting] = useState(false);
  const syncStartedRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;
    const ctrl = new AbortController();

    async function tick() {
      let report: BootService[] | null = null;
      try {
        const r = await fetchBootReport();
        report = r.services;
        if (cancelled) return;
        setServices(r.services);
      } catch {
        // Backend unreachable — show last-known state (or "checking…" placeholder)
        // and keep polling. This covers the "backend went down mid-session" case
        // the user called out.
      }

      const blockers = (report ?? []).filter(isBlocking);
      const allClear = report !== null && blockers.length === 0;

      if (allClear && !syncStartedRef.current) {
        syncStartedRef.current = true;
        const brokerCount = report?.filter(isBrokerRow).length ?? 0;
        runSync(ctrl.signal, brokerCount, qc).finally(() => {
          if (!cancelled) setSynced(true);
        });
        return; // stop polling — boot is done, sync owns the rest
      }

      if (!cancelled) timer = setTimeout(tick, POLL_MS);
    }

    tick();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
      ctrl.abort();
    };
  }, [qc]);

  // Once sync finishes, play the exit animation, then unmount the screen.
  useEffect(() => {
    if (!synced || exited) return;
    setExiting(true);
    const t = setTimeout(() => setExited(true), 500);
    return () => clearTimeout(t);
  }, [synced, exited]);

  if (exited) return <>{children}</>;

  const steps = services?.map(toStep) ?? PLACEHOLDER_STEPS;

  // While booting we do NOT mount `children` — mounting the dashboard
  // underneath fires its queries (holdings, watchlist, prices) immediately,
  // which both wastes a request roundtrip and creates a race when the user
  // navigates mid-boot. The whole point of the gate is "nothing runs until
  // probes pass," so just render the splash.
  return (
    <BootScreen
      steps={steps}
      live
      syncReady={synced}
      exiting={exiting}
      onDone={() => setExited(true)}
    />
  );
}

// Shown for the first frame before the first /health/boot response lands.
// Status "warn" + neutral detail so the splash doesn't flash green-then-red.
const PLACEHOLDER_STEPS: BootStep[] = [
  { key: "backend", label: "Backend · FastAPI gateway", status: "warn", doneStatus: "checking…" },
  { key: "vault", label: "Secrets · afbach vault", status: "warn", doneStatus: "checking…" },
  { key: "database", label: "Database · Postgres ready", status: "warn", doneStatus: "checking…" },
  { key: "llm", label: "AI Gateway · LLM routing", status: "warn", doneStatus: "checking…" },
];
