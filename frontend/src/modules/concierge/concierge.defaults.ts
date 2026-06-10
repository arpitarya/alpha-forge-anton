import { type ModelMeta, PROVIDER_ORDER, PROVIDERS, type ProviderId } from "./concierge.providers";
import { DEFAULT_POLICY } from "./concierge.registry.generated";

/** A concrete, pinned selection — never the `auto` router. Assignable to the
 *  pinned arm of `ModelChoice`. */
export interface DefaultChoice {
  provider: ProviderId;
  model: string;
}

// ── Default-model selection ─────────────────────────────────────────────────
// The default is what a fresh session (or a cleared model store) lands on, so it
// must be safe to fire unprompted and must NOT change as the user types. We
// DERIVE it from provider metadata instead of hardcoding a model id, so the right
// default re-emerges as providers/models/costs change. Criteria, heaviest first:
//   1. cost    — free before free* before paid (never spend without an explicit pick)
//   2. tag     — favour fast general-purpose over ultra-fast-but-small or deep/paid
//   3. context — longer context breaks ties (richer default input headroom)
//   4. order   — PROVIDER_ORDER as the final, stable tiebreak
// The weights are authored in the registry manifest (routing.json `default_policy`)
// and surfaced here via codegen. Documented in Fux: rule `concierge-default-model`.

const COST_SCORE: Record<string, number> = DEFAULT_POLICY.costScore;
const TAG_SCORE: Record<string, number> = DEFAULT_POLICY.tagScore;

function ctxScore(ctx: string): number {
  const m = /([\d.]+)\s*([mk])/i.exec(ctx);
  if (!m) return 0;
  const n = Number.parseFloat(m[1]);
  return m[2].toLowerCase() === "m" ? n * 1000 : n;
}

function score(provider: ProviderId, m: ModelMeta): number {
  const cost = COST_SCORE[m.cost] ?? 0;
  const tag = TAG_SCORE[m.tag] ?? 0;
  const order = PROVIDER_ORDER.length - PROVIDER_ORDER.indexOf(provider);
  // Weighted so a higher-priority criterion can never lose to a lower one.
  return cost * 1e6 + tag * 1e4 + ctxScore(m.ctx) + order;
}

/** Picks the pinned default by scoring every provider's models. Pure and
 *  deterministic — no I/O, no clock — so the default is stable across reloads. */
export function pickDefaultChoice(): DefaultChoice {
  let best: DefaultChoice | null = null;
  let bestScore = -1;
  for (const provider of PROVIDER_ORDER) {
    for (const m of PROVIDERS[provider].models) {
      const s = score(provider, m);
      if (s > bestScore) {
        bestScore = s;
        best = { provider, model: m.id };
      }
    }
  }
  // PROVIDERS is non-empty by construction; fall back defensively to Gemini Flash.
  return best ?? { provider: "gemini", model: "gemini-flash-latest" };
}
