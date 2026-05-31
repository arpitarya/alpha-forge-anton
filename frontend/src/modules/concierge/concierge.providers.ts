export type ProviderId =
  | "gemini"
  | "groq"
  | "cerebras"
  | "mistral"
  | "openrouter"
  | "huggingface"
  | "claude-sdk";

export interface ModelMeta {
  id: string;
  name: string;
  tag: string;
  ctx: string;
  cost: string;
  desc: string;
}

export interface ProviderMeta {
  id: ProviderId;
  name: string;
  vendor: string;
  glyph: string;
  desc: string;
  models: ModelMeta[];
}

export const PROVIDERS: Record<ProviderId, ProviderMeta> = {
  gemini: {
    id: "gemini",
    name: "Gemini",
    vendor: "Google · AI Studio",
    glyph: "G",
    desc: "Multimodal, long context, generous free tier.",
    models: [
      {
        id: "gemini-flash-latest",
        name: "Gemini Flash",
        tag: "fast",
        ctx: "1M ctx",
        cost: "free",
        desc: "Default — vision + PDF native, fast.",
      },
      {
        id: "gemini-2.5-pro",
        name: "Gemini 2.5 Pro",
        tag: "deep",
        ctx: "2M ctx",
        cost: "free*",
        desc: "Deep reasoning, free-tier limits apply.",
      },
    ],
  },
  groq: {
    id: "groq",
    name: "Groq",
    vendor: "groq.com · LPU",
    glyph: "Gq",
    desc: "Llama on LPUs — extreme low-latency.",
    models: [
      {
        id: "llama-3.3-70b-versatile",
        name: "Llama 3.3 70B",
        tag: "fast",
        ctx: "128k ctx",
        cost: "free",
        desc: "~200 tok/s, default workhorse for factoid.",
      },
    ],
  },
  cerebras: {
    id: "cerebras",
    name: "Cerebras",
    vendor: "cerebras.ai · WSE",
    glyph: "Cb",
    desc: "Wafer-scale inference, fastest free tier.",
    models: [
      {
        id: "llama3.1-8b",
        name: "Llama 3.1 8B",
        tag: "ultra-fast",
        ctx: "128k ctx",
        cost: "free",
        desc: "~2000 tok/s, ideal for news + lookups.",
      },
    ],
  },
  mistral: {
    id: "mistral",
    name: "Mistral",
    vendor: "mistral.ai · EU",
    glyph: "M",
    desc: "Structured output + JSON mode.",
    models: [
      {
        id: "mistral-small-latest",
        name: "Mistral Small",
        tag: "balanced",
        ctx: "128k ctx",
        cost: "free*",
        desc: "Strong at JSON schema + finance reasoning.",
      },
    ],
  },
  openrouter: {
    id: "openrouter",
    name: "OpenRouter",
    vendor: "openrouter.ai · aggregator",
    glyph: "OR",
    desc: "Aggregator — many free-tier models behind one key.",
    models: [
      {
        id: "google/gemma-4-26b-a4b-it:free",
        name: "Gemma 4 26B",
        tag: "free",
        ctx: "128k ctx",
        cost: "free",
        desc: "Default :free model — broad capability.",
      },
    ],
  },
  huggingface: {
    id: "huggingface",
    name: "HuggingFace",
    vendor: "hf.co · Inference",
    glyph: "Hf",
    desc: "Open-source serverless inference.",
    models: [
      {
        id: "mistralai/Mistral-7B-Instruct-v0.3",
        name: "Mistral 7B",
        tag: "open",
        ctx: "32k ctx",
        cost: "free",
        desc: "Fallback / experimental open-weights.",
      },
    ],
  },
  "claude-sdk": {
    id: "claude-sdk",
    name: "Claude",
    vendor: "Anthropic · paid",
    glyph: "C",
    desc: "Strongest reasoning — gated by CostGuard.",
    models: [
      {
        id: "claude-sonnet-4-6",
        name: "Claude Sonnet 4.6",
        tag: "paid",
        ctx: "200k ctx",
        cost: "$3/M",
        desc: "Confirmation required before each call.",
      },
    ],
  },
};

export const PROVIDER_ORDER: ProviderId[] = [
  "gemini",
  "groq",
  "cerebras",
  "mistral",
  "openrouter",
  "huggingface",
  "claude-sdk",
];
