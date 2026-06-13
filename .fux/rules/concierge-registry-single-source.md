---
id: concierge-registry-single-source
domain: concierge
type: convention
status: active
created: 2026-06-10
updated: 2026-06-13
keywords:
  - registry
  - providers
  - routing
  - intent
  - chain
  - manifest
  - codegen
  - single-source
  - drift
  - consumption
  - pricing
  - max_tokens
  - cost_guard
code_refs:
  - concierge/llm/src/alphaforge_anton_llm/registry/providers.json
  - concierge/llm/src/alphaforge_anton_llm/registry/routing.json
  - concierge/llm/src/alphaforge_anton_llm/registry.py
  - concierge/llm/src/alphaforge_anton_llm/pricing.py
  - concierge/llm/src/alphaforge_anton_llm/cost_guard.py
  - concierge/llm/src/alphaforge_anton_llm/providers/base.py
  - frontend/scripts/gen-concierge-registry.mjs
  - frontend/src/modules/concierge/concierge.registry.generated.ts
related:
  - concierge-default-model
  - orff
  - ui-component-contract
  - files-max-100-lines
---
**Convention:** The concierge **provider/model registry, intent→provider routing,
and default-model policy** have exactly one authoritative source: the JSON manifest
in the gateway package — `alphaforge_anton_llm/registry/{providers.json,
routing.json}`. Python (the gateway `router.py` and the backend concierge module)
reads it natively via `registry.py` (`importlib.resources`). The frontend never
hand-maintains this data: `gen-concierge-registry.mjs` generates
`concierge.registry.generated.ts` from the same JSON, and
`concierge.providers.ts` / `concierge.routing.ts` / `concierge.defaults.ts` are thin
adapters over the generated module. `pnpm build` regenerates first; `--check` mode
fails CI if the committed file is stale.

**The manifest drives runtime, not just the picker.** Each model carries a
`consumption` block (`input_per_m`, `output_per_m`, `max_tokens`, `paid`). Provider
adapters no longer hardcode a `_MODEL` constant: `base.ProviderAdapter.default_model`
reads `registry.default_model(name)` (the first model in `providers.json`), and a
per-call `model` override flows gateway → adapter (the frontend `model_id` pin is
honoured end-to-end, but only on its own provider — a privacy floor or Auto override
drops it). `pricing.py` is the one interpreter of `consumption`: `CostGuard` gates on
`pricing.is_paid` (no hardcoded paid-provider set), adapters cap output with
`pricing.max_tokens`, and `pricing.estimate_cost_usd` turns token counts into real
spend. So the model the picker shows, the model that runs, and the model that's
priced are guaranteed the same id.

**Why:** The registry previously lived in three independently edited
representations — frontend `concierge.providers.ts` + `resolveTopAuto`, backend
`_QUERY_TYPE_BY_INTENT` + `PROVIDER_TO_QUERY_TYPE`, and the gateway `_DEFAULT_CHAINS`
— which drifted in practice: a "risk/portfolio" query previewed as **Gemini** in the
picker while the gateway actually routed it to **Mistral**. A self-hosted terminal
where the displayed model and the model that answers disagree is a correctness and
trust bug. One manifest, two derived consumers, makes them impossible to diverge —
this is "all the concierge logic lives in concierge" expressed as *one source of
knowledge*, not one directory (frameworks pin the backend/frontend code in place;
see [[ui-component-contract]] for the parallel registry-driven pattern).

**Canonical-behavior rule:** the **gateway chains win** — the frontend Auto preview
shows the true chain head. To change routing, edit `routing.json`, never code.

**How to apply:** Add/remove a model or reprice one → edit its entry in
`providers.json`, including the `consumption` block (`input_per_m`, `output_per_m`,
`max_tokens`, `paid`) — never touch a `_MODEL` constant (there are none) or the
`CostGuard` paid list (there is none). The first model in a provider's list is its
default; reorder to change the default. Add/remove a provider → edit `providers.json`.
Change routing → edit `routing.json` (`intents` patterns, `chains`,
`provider_query_type`) or the `default_policy` weights. Then `pnpm gen:concierge`
(or `just gen-concierge`) to refresh the generated TS, and `just test-backend` to
revalidate parity. Never
edit `concierge.registry.generated.ts` by hand, and never re-add a provider list or
routing table to a `.ts`/`.py` file. `concierge_schemas.ProviderSlug` stays a static
`Literal` (Pydantic needs it) but asserts equality with `registry.provider_slugs()`
at import, so any drift fails loudly.
