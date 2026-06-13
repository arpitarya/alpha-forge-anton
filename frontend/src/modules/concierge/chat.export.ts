import type { ChatTurn } from "./concierge.types";

/** Render a thread to Markdown — a local, shareable snapshot of the session. */
export function threadToMarkdown(turns: ChatTurn[]): string {
  const lines = [
    `# Orff conversation`,
    `_${turns.length} turns · exported ${new Date().toISOString()}_`,
    "",
  ];
  for (const t of turns) {
    lines.push(`## You`, t.query, "");
    if (t.thinking) lines.push(`> _reasoning:_ ${t.thinking}`, "");
    lines.push(`## Orff${t.provider ? ` (${t.provider})` : ""}`, t.response ?? "_(no reply)_", "");
    if (t.followups?.length) lines.push(`_Suggested:_ ${t.followups.join(" · ")}`, "");
  }
  return lines.join("\n");
}

/** Trigger a client-side download of the thread as a .md file. */
export function downloadThread(turns: ChatTurn[]): void {
  if (typeof window === "undefined" || !turns.length) return;
  const blob = new Blob([threadToMarkdown(turns)], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `orff-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
