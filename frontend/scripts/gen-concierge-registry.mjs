#!/usr/bin/env node
// Generates concierge.registry.generated.ts from the gateway's registry manifest —
// the single source of truth (Fux: concierge-registry-single-source). Never edit
// the generated file by hand. Run: pnpm gen:concierge   (CI parity: --check)
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const REGISTRY = join(here, "../../concierge/llm/src/alphaforge_anton_llm/registry");
const OUT = join(here, "../src/modules/concierge/concierge.registry.generated.ts");

const providers = JSON.parse(readFileSync(join(REGISTRY, "providers.json"), "utf-8"));
const routing = JSON.parse(readFileSync(join(REGISTRY, "routing.json"), "utf-8"));

const order = providers.order;
// Inject the slug as `id` on each provider (the manifest keys it, the type carries it).
const PROVIDERS = Object.fromEntries(
  order.map((slug) => [slug, { id: slug, ...providers.providers[slug] }]),
);
const INTENT_PATTERNS = routing.intents.map((i) => ({
  pattern: i.pattern,
  queryType: i.query_type,
}));
const DEFAULT_POLICY = {
  costScore: routing.default_policy.cost_score,
  tagScore: routing.default_policy.tag_score,
};

const union = order.map((s) => JSON.stringify(s)).join(" | ");
const lit = (v) => JSON.stringify(v, null, 2);

const content = `// GENERATED — do not edit. Source: concierge/llm/src/alphaforge_anton_llm/registry/{providers,routing}.json
// Regenerate: pnpm gen:concierge  (Fux: concierge-registry-single-source)

export type ProviderId = ${union};

export interface ModelConsumption {
  input_per_m: number;
  output_per_m: number;
  max_tokens: number;
  paid: boolean;
}

export interface ModelMeta {
  id: string;
  name: string;
  tag: string;
  ctx: string;
  cost: string;
  desc: string;
  consumption: ModelConsumption;
}

export interface ProviderMeta {
  id: ProviderId;
  name: string;
  vendor: string;
  glyph: string;
  desc: string;
  models: ModelMeta[];
}

export const PROVIDERS: Record<ProviderId, ProviderMeta> = ${lit(PROVIDERS)};

export const PROVIDER_ORDER: ProviderId[] = ${lit(order)};

export interface IntentPattern {
  pattern: string;
  queryType: string;
}

export const INTENT_PATTERNS: IntentPattern[] = ${lit(INTENT_PATTERNS)};

export const FALLBACK_QUERY_TYPE = ${JSON.stringify(routing.fallback_query_type)};

export const CHAINS: Record<string, ProviderId[]> = ${lit(routing.chains)};

export const DEFAULT_POLICY = ${lit(DEFAULT_POLICY)} as const;
`;

if (process.argv.includes("--check")) {
  const current = readFileSync(OUT, "utf-8");
  if (current !== content) {
    console.error("✗ concierge.registry.generated.ts is stale — run `pnpm gen:concierge`");
    process.exit(1);
  }
  console.log("✔ concierge registry in sync");
} else {
  writeFileSync(OUT, content);
  console.log(`✔ wrote ${OUT}`);
}
