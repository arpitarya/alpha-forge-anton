---
id: project-fux
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-06-02
updated: 2026-06-09
---
Fux is a sibling tool (beside wagner/bach/orff) at `~/my_programs/fux` (remote
`git@github.com:arpitarya/fux.git`). It is a portable, Claude-aware **knowledge
engine**: one frontmatter substrate in a project's `.fux/` → derived INDEX + graph
+ memory views, with $0 deterministic maintenance (Python stdlib only).

The design plan lives **only in the fux repo** at `fux/docs/fux-plan.md` (moved
out of `anton/docs/` 2026-06-09 — no longer mirrored in Anton). Fux **replaces**
three things Anton runs separately — graphify (`graphify-out/`), cross-session
memory (this dir), and the narrative docs — and adds the business-rules layer none
held. Plan §18 frames Fux as Anton's **brain** serving two consumers over one MCP
interface: Claude Code (dev-time) and the Orff concierge (runtime).

**On-the-fly UI generation is shipped end-to-end (2026-06-09), safe by construction
— Orff emits a declarative UISpec (JSON tree), never code.** Engine commands:
`fux impact`, `fux components`, `fux validate-spec` (mount-time guardrail), `fux
feedback` (learning loop) — all over MCP. Anton: `POST /concierge/compose`
(`compose_service.py` + `fux_bridge.py` → `fux` CLI), frontend `DynamicRenderer.tsx`
renders only whitelisted `@alphaforge-anton/solar-ui` primitives (`compose.registry.ts`).
The `ui-component-contract` rule governs the loop. No code path executes model output.

**Why:** future Anton sessions may be asked to adopt Fux or migrate the existing
stores into it.
**How to apply:** if asked to "set up fux here" / migrate graphify or memory,
the engine + `/fux` skill live in the fux repo; run `fux init` in Anton. See
[[project-broker-prime]] and [[project-wagner-dante]] for adjacent context.
