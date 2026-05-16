export type ModelId =
  | "auto"
  | "gemini"
  | "groq"
  | "claude-sdk"
  | "cerebras"
  | "mistral"
  | "openrouter"
  | "huggingface";

export interface ModelMeta {
  name: string;
  tag: string;
  description: string;
}

export const MODELS: Record<Exclude<ModelId, "auto">, ModelMeta> = {
  gemini: {
    name: "Gemini",
    tag: "google",
    description: "Gemini Flash / Pro — fast multimodal reasoning from Google.",
  },
  groq: {
    name: "Groq",
    tag: "fast",
    description: "Llama & Mixtral on Groq — extremely low-latency inference.",
  },
  "claude-sdk": {
    name: "Claude Sonnet",
    tag: "anthropic",
    description: "Claude Sonnet — nuanced analysis and long-form reasoning.",
  },
  cerebras: {
    name: "Cerebras",
    tag: "ultra-fast",
    description: "Llama on Cerebras wafer — fastest token throughput available.",
  },
  mistral: {
    name: "Mistral",
    tag: "eu",
    description: "Mistral models — efficient European AI, strong at finance.",
  },
  openrouter: {
    name: "OpenRouter",
    tag: "multi",
    description: "Routes to GPT-4o, Command R+, and other frontier models.",
  },
  huggingface: {
    name: "HuggingFace",
    tag: "open",
    description: "Open-source models via HuggingFace Inference API.",
  },
};

export function resolveAutoModel(query: string): Exclude<ModelId, "auto"> {
  if (/risk|drawdown|var|simulat|scenario|stress|exposure|rebalanc|hedge|tax|optim/i.test(query))
    return "claude-sdk";
  if (/screen|scan|breakout|filter|quote|ltp|price of|list|ticker|search/i.test(query))
    return "cerebras";
  if (/private|on.?device|local|offline|sensitive|personal/i.test(query)) return "mistral";
  return "gemini";
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
  resolvedModel: Exclude<ModelId, "auto">;
}
