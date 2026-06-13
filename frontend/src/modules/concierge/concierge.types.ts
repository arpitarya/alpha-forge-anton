import type { UINode } from "./compose.types";
import { PROVIDERS, type ProviderId } from "./concierge.providers";
import { resolveProviderAuto, resolveTopAuto } from "./concierge.routing";

export type { ModelMeta, ProviderId, ProviderMeta } from "./concierge.providers";
export { PROVIDER_ORDER, PROVIDERS } from "./concierge.providers";
export { resolveProviderAuto, resolveTopAuto } from "./concierge.routing";

export type AutoLevel = "top" | "provider" | "none";

/**
 * Two-level model selection.
 * - `{ provider: "auto" }` — top-level Auto, routes across all providers.
 * - `{ provider, model: "auto" }` — provider Auto, picks within that provider.
 * - `{ provider, model }` — fully pinned.
 */
export type ModelChoice =
  | { provider: "auto" }
  | { provider: ProviderId; model: "auto" }
  | { provider: ProviderId; model: string };

export interface ActiveModel {
  provider: ProviderId;
  modelId: string;
  providerName: string;
  modelName: string;
  autoLevel: AutoLevel;
}

export function activeModelFor(choice: ModelChoice, query: string): ActiveModel {
  if (choice.provider === "auto") {
    const r = resolveTopAuto(query);
    return {
      provider: r.provider,
      modelId: r.modelId,
      providerName: PROVIDERS[r.provider].name,
      modelName: lookup(r.provider, r.modelId),
      autoLevel: "top",
    };
  }
  if (choice.model === "auto") {
    const modelId = resolveProviderAuto(choice.provider, query);
    return {
      provider: choice.provider,
      modelId,
      providerName: PROVIDERS[choice.provider].name,
      modelName: lookup(choice.provider, modelId),
      autoLevel: "provider",
    };
  }
  return {
    provider: choice.provider,
    modelId: choice.model,
    providerName: PROVIDERS[choice.provider].name,
    modelName: lookup(choice.provider, choice.model),
    autoLevel: "none",
  };
}

function lookup(provider: ProviderId, modelId: string): string {
  return PROVIDERS[provider].models.find((m) => m.id === modelId)?.name ?? modelId;
}

export function formatChoiceLabel(active: ActiveModel): string {
  if (active.autoLevel === "top") return `Auto → ${active.modelName}`;
  if (active.autoLevel === "provider") return `${active.providerName} / Auto → ${active.modelName}`;
  return `${active.providerName} · ${active.modelName}`;
}

/** A prompt-assembly / data-read step, surfaced as a collapsible tool block. */
export interface ToolStep {
  name: string;
  detail: string;
  ms: number;
}

/** A mutating intent Orff detected — rendered as a structured approval card. */
export interface PendingAction {
  id: string;
  action: string;
  summary: string;
  steps: string[];
}

export interface ChatTurn {
  id: string;
  query: string;
  response: string | null;
  provider: string | null;
  model: string | null;
  elapsed: number | null;
  tokens: number | null;
  error: string | null;
  loading: boolean;
  active: ActiveModel;
  /** Fux-validated UISpec attached by the compose follow-up (§18.3). */
  spec?: UINode | null;
  /** Reasoning trace split from a `<think>` block on reasoning models. */
  thinking?: string | null;
  /** Data-read trail (Fux recall, memory load, holdings disclosure, …). */
  tools?: ToolStep[];
  /** Approval card for a detected mutating intent. */
  confirm?: PendingAction | null;
  /** Tap-to-send next-step prompts. */
  followups?: string[];
  /** Real USD spend for the turn (0 on free providers). */
  costUsd?: number | null;
  /** Image data URLs the user attached to the prompt. */
  images?: string[];
}
