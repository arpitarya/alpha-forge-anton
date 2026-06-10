import {
  CHAINS,
  FALLBACK_QUERY_TYPE,
  INTENT_PATTERNS,
  PROVIDERS,
  type ProviderId,
} from "./concierge.registry.generated";

export interface Resolved {
  provider: ProviderId;
  modelId: string;
}

// Intent classification + the QueryType→provider chains are authored in the
// registry manifest (single source of truth). The gateway is the real router, so
// the Auto preview shows the true chain head — see Fux concierge-registry-single-source.
function classifyIntent(q: string): string {
  const s = (q || "").toLowerCase();
  for (const { pattern, queryType } of INTENT_PATTERNS) {
    if (new RegExp(pattern, "i").test(s)) return queryType;
  }
  return FALLBACK_QUERY_TYPE;
}

/** A provider's default model — the first entry in its model list. */
function providerDefault(provider: ProviderId): string {
  return PROVIDERS[provider].models[0].id;
}

export function resolveTopAuto(q: string): Resolved {
  const chain = CHAINS[classifyIntent(q)] ?? ["gemini"];
  const provider = chain[0];
  return { provider, modelId: providerDefault(provider) };
}

export function resolveProviderAuto(provider: ProviderId, _q: string): string {
  return providerDefault(provider);
}
