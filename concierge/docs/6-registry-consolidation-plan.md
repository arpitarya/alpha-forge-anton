# 6 — Concierge registry consolidation

**Status:** in progress · **Decision owner:** registry is the single source of truth.

## Why

"Concierge" logic is spread across four trees — the top-level `concierge/` package
+ docs, `backend/app/modules/concierge/`, `frontend/src/modules/concierge/`, and the
Next.js proxy route. A literal relocation is impossible: FastAPI's `app.modules.*`
imports and Next.js filesystem routing pin the backend/frontend code in place.

The real scatter worth fixing is **duplicated knowledge**. The provider/model
registry and the intent→provider routing existed in three independent, hand-synced
representations that already drifted:

| Concern | frontend | backend | gateway |
|---|---|---|---|
| Provider/model registry | `concierge.providers.ts` | `concierge_schemas.py` (`ProviderSlug`) | `providers/` adapters + `docs/providers.md` |
| Query text → intent | `concierge.routing.ts` (`resolveTopAuto`) | `concierge_service.py` (`_QUERY_TYPE_BY_INTENT`) | — |
| Intent → provider chain | (collapsed into `resolveTopAuto`) | `concierge_schemas.py` (`PROVIDER_TO_QUERY_TYPE`) | `router.py` (`_DEFAULT_CHAINS`) |
| Default-model policy | `concierge.defaults.ts` | — | — |

**Concrete drift:** a "risk/portfolio" query previewed as **Gemini** in the
frontend, but the gateway actually routed it to **Mistral** (`INVESTMENT_PLAN`
chain head). One authoritative manifest, consumed by both runtimes, makes the
picker preview, the backend classifier, and the gateway chains impossible to
disagree.

## Canonical-behavior decision

The gateway is the *real* router, so **the gateway chains win**. After
consolidation the frontend Auto preview shows the true chain head. To change a
head, edit `routing.json` — not code. Low day-to-day impact: the default is now
*pinned* (see [`concierge-default-model`]), so the top-Auto preview only appears
when the user explicitly selects Auto.

## Authoritative home

Inside the gateway package, so Python reads it natively (`importlib.resources`,
ships in the wheel) and the frontend generates from the same JSON:

```
concierge/llm/src/alphaforge_anton_llm/registry/
  providers.json   # ordered slugs + per-provider meta + models[{id,name,tag,ctx,cost,desc}]
  routing.json     # intents[{pattern,query_type}] · chains{query_type:[slug]} ·
                   # provider_query_type{slug:qt} · default_policy{cost_score,tag_score}
```

## Plan

0. **This doc + Fux entries first** — `concierge-registry-single-source` (new) and
   `concierge-default-model` (updated). Knowledge leads the change.
1. **Author the manifest** — lift `PROVIDERS`/`PROVIDER_ORDER`, `_DEFAULT_CHAINS`,
   `_QUERY_TYPE_BY_INTENT`, `PROVIDER_TO_QUERY_TYPE`, and the default-policy weights
   into the two JSON files verbatim (data move, no logic change).
2. **Python loader** — `alphaforge_anton_llm/registry.py` (≤100 lines):
   `load_providers`, `provider_order`, `provider_slugs`, `classify_intent`,
   `chain_for`, `provider_query_type`, `default_choice`.
3. **Wire Python consumers** — `router.py` seeds `_DEFAULT_CHAINS` from the manifest
   (eval overrides still layer on top); `concierge_service.py` uses
   `classify_intent`; `concierge_schemas.py` keeps `ProviderSlug` as a `Literal`
   but asserts it equals `provider_slugs() | {"auto"}` at import.
4. **Frontend codegen** — `frontend/scripts/gen-concierge-registry.mjs` emits
   `concierge.registry.generated.ts` (committed) and supports `--check`. `pnpm build`
   runs it first.
5. **Thin frontend adapters** — `concierge.providers.ts`, `concierge.routing.ts`,
   `concierge.defaults.ts` re-export / consume the generated module.
6. **Docs + Fux** — point `README.md` + `docs/providers.md` at the manifest;
   `fux build && fux check`; `graphify update .`.

## Verification

- `just test-backend` — new `test_concierge_registry.py` (chain providers exist,
  every provider has ≥1 model, `default_choice` → `gemini-flash-latest`,
  `classify_intent` returns expected `QueryType`s).
- Frontend: `pnpm gen:concierge` → `pnpm type-check` + `biome check`;
  `just gen-concierge-check` proves the committed generated file is in sync.
- Probe: footer model label stable while typing + Gemini Flash default; Auto preview
  matches the backend route for a "risk" query. New `just` recipe.

## Out of scope

- No physical relocation of backend/frontend modules.
- No change to provider adapters, cost guard, or the SSE protocol.
- Existing `af-model-choice` localStorage values left untouched.
