import { PROVIDERS, type ProviderId } from "./concierge.providers";

export interface Resolved {
  provider: ProviderId;
  modelId: string;
}

const PROVIDER_DEFAULT: Record<ProviderId, string> = {
  gemini: "gemini-flash-latest",
  groq: "llama-3.3-70b-versatile",
  cerebras: "llama3.1-8b",
  mistral: "mistral-small-latest",
  openrouter: "google/gemma-4-26b-a4b-it:free",
  huggingface: "mistralai/Mistral-7B-Instruct-v0.3",
  "claude-sdk": "claude-sonnet-4-6",
};

export function resolveTopAuto(q: string): Resolved {
  const s = (q || "").toLowerCase();
  if (!s) return { provider: "gemini", modelId: PROVIDER_DEFAULT.gemini };
  if (
    /risk|drawdown|var|simulat|scenario|stress|exposure|rebalanc|hedge|tax|optim|portfolio/.test(s)
  )
    return { provider: "gemini", modelId: PROVIDER_DEFAULT.gemini };
  if (/news|today|latest|breaking|happening|sector|industry|earning|result/.test(s))
    return { provider: "cerebras", modelId: PROVIDER_DEFAULT.cerebras };
  if (/screen|scan|breakout|filter|quote|ltp|price of|list|ticker|search/.test(s))
    return { provider: "cerebras", modelId: PROVIDER_DEFAULT.cerebras };
  if (/json|schema|structured/.test(s))
    return { provider: "mistral", modelId: PROVIDER_DEFAULT.mistral };
  return { provider: "groq", modelId: PROVIDER_DEFAULT.groq };
}

export function resolveProviderAuto(provider: ProviderId, _q: string): string {
  const list = PROVIDERS[provider].models;
  return PROVIDER_DEFAULT[provider] && list.some((m) => m.id === PROVIDER_DEFAULT[provider])
    ? PROVIDER_DEFAULT[provider]
    : list[0].id;
}
