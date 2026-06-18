---
id: orff
domain: concierge
type: glossary
status: active
created: 2026-06-09
updated: 2026-06-19
aliases:
  - concierge
  - assistant
  - AI layer
keywords:
  - orff
  - concierge
  - llm
  - gateway
  - compose
  - uispec
code_refs:
  - concierge/README.md
related:
  - ui-component-contract
  - project-fux
---
**Term:** Orff

**Definition:** The conversational AI layer inside Anton — a persistent,
session-aware financial assistant over the free-provider `llm.gateway` stack, named
for Carl Orff (composer naming: Anton, Wagner, Dante, Orff). Memory lives in
`concierge_sessions` / `concierge_turns`; replies stream over SSE. Orff can also
**compose UI on the fly**: it emits a declarative UISpec (a JSON tree, never code)
that Fux validates against the component registry and the frontend renders from a
whitelist — governed by [[ui-component-contract]]. The brain it queries is Fux
([[project-fux]]).
