// Thin adapter over the generated registry — the provider/model data is authored
// in concierge/llm/.../registry/providers.json (single source of truth). Edit the
// manifest + `pnpm gen:concierge`, never this file. See Fux:
// concierge-registry-single-source.
export type { ModelMeta, ProviderId, ProviderMeta } from "./concierge.registry.generated";
export { PROVIDER_ORDER, PROVIDERS } from "./concierge.registry.generated";
