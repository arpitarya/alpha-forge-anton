/**
 * Slash-command registry — the Claude-Code affordance: typed shortcuts that
 * either expand into a prompt (`send`) or fire a client action (`action`),
 * bypassing free-text routing. Surfaced inline (CommandMenu) and via Cmd+K
 * (CommandPalette). One source so both menus and the parser agree.
 */
export type CommandKind =
  | { kind: "send"; prompt: string }
  | { kind: "action"; action: CommandAction };

export type CommandAction =
  | "export"
  | "memory"
  | "history"
  | "artifacts"
  | "clear"
  | "stop"
  | "voice"
  | "proposal";

export interface SlashCommand {
  name: string;
  hint: string;
  body: CommandKind;
}

export const COMMANDS: SlashCommand[] = [
  {
    name: "review",
    hint: "Buy/hold/trim/sell vs your last plan",
    body: {
      kind: "send",
      prompt: "Review every holding vs my last plan — buy/hold/trim/sell with reasons and stops.",
    },
  },
  {
    name: "screen",
    hint: "Screen new swing entries in your themes",
    body: { kind: "send", prompt: "Screen for new swing entries in my themes." },
  },
  {
    name: "rebalance",
    hint: "Draft a rebalance toward plan targets",
    body: {
      kind: "send",
      prompt: "Rebalance my portfolio toward the plan targets and show the diff.",
    },
  },
  {
    name: "projection",
    hint: "Project portfolio value forward 10y",
    body: { kind: "send", prompt: "Project my portfolio value forward 10 years at the plan mix." },
  },
  {
    name: "risk",
    hint: "Drawdown, concentration, exposure",
    body: {
      kind: "send",
      prompt: "What's my portfolio risk right now? Cover drawdown and concentration.",
    },
  },
  {
    name: "networth",
    hint: "Live net-worth card",
    body: { kind: "send", prompt: "Show my live net worth as a card." },
  },
  {
    name: "refresh",
    hint: "Sync brokers and refresh holdings",
    body: { kind: "send", prompt: "Sync my broker sources and refresh holdings." },
  },
  { name: "memory", hint: "Edit what Orff remembers", body: { kind: "action", action: "memory" } },
  {
    name: "history",
    hint: "Browse & resume past chats",
    body: { kind: "action", action: "history" },
  },
  {
    name: "artifacts",
    hint: "Open composed UI panel",
    body: { kind: "action", action: "artifacts" },
  },
  {
    name: "proposal",
    hint: "Demo: downside-first cone + approval (mock)",
    body: { kind: "action", action: "proposal" },
  },
  { name: "export", hint: "Download this thread", body: { kind: "action", action: "export" } },
  { name: "clear", hint: "Clear the conversation", body: { kind: "action", action: "clear" } },
  { name: "stop", hint: "Stop generating", body: { kind: "action", action: "stop" } },
];

/** Commands whose name starts with the text after a leading "/". */
export function matchCommands(input: string): SlashCommand[] {
  if (!input.startsWith("/")) return [];
  const q = input.slice(1).toLowerCase().trim();
  return COMMANDS.filter((c) => c.name.startsWith(q) || c.hint.toLowerCase().includes(q));
}

/** Resolve a fully-typed "/name" to its command, else null. */
export function resolveCommand(input: string): SlashCommand | null {
  if (!input.startsWith("/")) return null;
  const name = input.slice(1).trim().toLowerCase();
  return COMMANDS.find((c) => c.name === name) ?? null;
}
