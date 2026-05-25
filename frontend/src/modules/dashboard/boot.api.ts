import api from "@/lib/api";
import type { BootReport, SyncResult } from "./boot.types";

/** Snapshot of every backend system the boot splash cares about. */
export async function fetchBootReport(): Promise<BootReport> {
  const res = await api.get<BootReport>("/health/boot");
  return res.data;
}

/** Stream per-broker sync results via SSE; calls onResult as each resolves.
 * Resolves when the stream closes (all brokers done or connection dropped). */
export async function streamBootSync(
  onResult: (slug: string, result: SyncResult) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
  const res = await fetch("/api/v1/health/boot/sync-stream", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    signal,
  });
  if (!res.ok || !res.body) return;

  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop() ?? "";
    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const ev = JSON.parse(line.slice(6)) as SyncResult & { slug: string };
      onResult(ev.slug, { ok: ev.ok, holdings_count: ev.holdings_count, detail: ev.detail });
    }
  }
}
