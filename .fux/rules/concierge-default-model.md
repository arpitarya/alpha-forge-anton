---
id: concierge-default-model
domain: concierge
type: convention
status: active
created: 2026-06-10
updated: 2026-06-10
code_refs:
  - frontend/src/modules/concierge/concierge.defaults.ts
  - frontend/src/modules/concierge/ChatContext.tsx
  - frontend/src/modules/concierge/concierge.routing.ts
  - concierge/llm/src/alphaforge_anton_llm/registry/routing.json
related: [concierge-registry-single-source, orff, ui-component-contract, files-max-100-lines]
keywords: [model-picker, default, auto, routing, gemini, provider, flicker, pinned]
---
**Convention:** A fresh Orff session pins a **derived default model**, never the
`auto` router. The default is computed by `pickDefaultChoice()` in
`concierge.defaults.ts`, which scores every provider's models and picks the
highest, ranked by — in strict priority — **cost** (free → free\* → paid),
**tag** (fast/balanced → ultra-fast → deep/open/paid), **context length**, then
`PROVIDER_ORDER`. The scoring **weights live in the manifest**
(`routing.json` `default_policy`), surfaced to the frontend as `DEFAULT_POLICY` via
codegen — see [[concierge-registry-single-source]]. Today that resolves to **Gemini
Flash** (free, fast, 1M ctx, multimodal). `ChatContext.loadChoice()` returns this
default whenever the
`af-model-choice` store is empty; an explicit prior pick — *including* Auto — is
always honoured.

**Why:** With `auto` as the default, the picker showed a **live routing preview**
that re-resolved on every keystroke via `resolveTopAuto` — empty box → Gemini,
generic text → the Groq/Llama fallback, clear → Gemini again. That flicker reads
as a bug ("the model keeps changing as I type"). Pinning a concrete model makes
the default **stable and predictable**: it changes only when the user changes it.
Deriving the default from metadata (instead of hardcoding `"gemini-flash-latest"`)
keeps it correct as providers, models, or free-tier costs change — and keeps the
"never spend money unprompted" guarantee tied to the `cost` field, parallel to
CostGuard gating on `claude-sdk`.

**How to apply:** Auto routing still exists and still previews per query — it is
now an explicit choice in the `ModelPicker`, not the default. To shift the default,
adjust the metadata in `concierge.providers.ts` (cost/tag/ctx) or the weights in
`concierge.defaults.ts`; do **not** hardcode a model id at the call site. The
backend `_resolve` in `concierge_service.py` already routes a pinned
`{provider, model}` directly, so no server change is needed — only `req.provider
== "auto"` triggers server-side intent classification.
