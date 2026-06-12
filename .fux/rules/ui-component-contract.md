---
id: ui-component-contract
domain: frontend
type: convention
status: active
created: 2026-06-09
updated: 2026-06-09
code_refs:
  - frontend/src/modules/concierge/DynamicRenderer.tsx
  - frontend/src/modules/concierge/compose.registry.ts
  - backend/app/modules/concierge/compose_service.py
related: [files-max-100-lines, async-everywhere]
keywords: [orff, compose, uispec, registry, generated, on-the-fly, sandbox]
---
**Convention:** A UI Orff generates on the fly is a **declarative UISpec** — a JSON
tree of `{component, props, data?, children?}` nodes — **never code**. Every node
must name a component in the Fux component registry (`fux components`), use only
that component's declared props, and bind live data only via a registry hook
(`data: "useHoldings"`). The spec is validated by `fux validate-spec` server-side
and rendered from the client whitelist in `compose.registry.ts`.

**Why:** Generating and `eval`-ing arbitrary TSX at runtime is an unbounded code-
execution hole in a self-hosted app that holds financial data. Constraining the
model to a declarative tree over a fixed whitelist makes generated UI **safe by
construction**: the worst a bad/compromised model can emit is a spec the validator
rejects — it can never introduce a new component, prop, side effect, or network
call. It also makes output born-compliant — every primitive is already functional,
themed, and ≤100 lines (see [[files-max-100-lines]]).

**How to apply:** New presentational primitives become composable by exporting them
from `@alphaforge-anton/solar-ui` *and* adding them to **both** halves of the curated
vocabulary: the client `WHITELIST` (`compose.registry.ts`) and the backend
`COMPOSABLE_COMPONENTS` (`compose_registry.py`); new data sources by a parameterless
`use*` hook added to `COMPOSABLE_HOOKS` + `SpecHost.tsx`. The two halves are kept
identical by `just probe compose-registry` — prompt = validator = whitelist. Anything
the model references outside the vocabulary is rejected, surfaced by `fux feedback`
as a candidate gap, never rendered. In chat, a turn matching the manifest's
`compose.pattern` (routing.json — single source) also gets a spec via
`compose_followup`, streamed as a separate SSE event and rendered by `SpecCard`.

**Worked example** — "a live net-worth card" composes to:

```json
{"component": "Card", "props": {"variant": "glow"}, "children": [
  {"component": "CountUp", "props": {"value": 4821000, "prefix": "₹"}, "data": "useHoldings"},
  {"component": "Badge", "props": {"children": "LIVE", "variant": "success"}}
]}
```

**Edge case:** a generated node with children but a component that declares no
`children` prop is rejected (`takes no children`) — the validator will not silently
drop them.
