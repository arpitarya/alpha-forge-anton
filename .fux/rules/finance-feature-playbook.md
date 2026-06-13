---
id: finance-feature-playbook
domain: process
type: convention
status: active
created: 2026-06-12
updated: 2026-06-13
aliases:
  - new-metric
  - finance-feature
  - end-to-end
keywords:
  - playbook
  - metric
  - feature
  - pipeline
  - checklist
code_refs:
  - backend/app/modules/plans/projection_service.py
  - backend/app/modules/concierge/compose_registry.py
  - frontend/src/modules/concierge/SpecHost.tsx
related:
  - ui-component-contract
  - doc-per-code-change
  - files-max-100-lines
  - probe-cdp-not-playwright
---
**Convention:** a new financial metric/insight ships through a fixed seven-step
pipeline — each step has an existing exemplar (the projection feature):

1. **Knowledge first** — write the Fux entry (formula/rule with `check:` and
   `examples:`) so the definition is citable before code exists. Exemplar:
   [[capital-market-assumptions]].
2. **Service** — pure async function in the owning module, ≤100 lines, reading
   committed knowledge not hard-coded constants. Exemplar:
   `projection_service.py`.
3. **Route** — thin endpoint with Pydantic v2 schemas. Exemplar:
   `plan_routes.py`.
4. **Hook** — parameterless `use*` in the frontend module + registered in
   `COMPOSABLE_HOOKS` and `SpecHost.tsx`. Exemplar: `useProjection`.
5. **Component (if needed)** — solar-ui primitive with JSON-serializable
   props, added to **both** whitelist halves ([[ui-component-contract]]).
6. **Probe** — standalone math/contract probe + `just` recipe; a feature is
   unverified until its probe is green ([[probe-cdp-not-playwright]]).
   Exemplar: `plan_projection_probe.py`.
7. **Docs** — architecture tree + this knowledge graph in the same session
   ([[doc-per-code-change]]).

**Why:** knowledge-first ordering means Orff can ground answers in the metric
the moment the endpoint exists, the validator/whitelist symmetry is preserved
by construction, and every figure the UI shows traces back to a committed,
testable definition — never an LLM improvisation.

**How to apply:** when asked to "add a metric/insight/chart", walk the steps
in order and name them in the plan; skipping the Fux entry or the probe is
what turns a feature into unverifiable output.
