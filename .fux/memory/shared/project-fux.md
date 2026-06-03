---
id: project-fux
domain: project
type: memory
subtype: project
scope: shared
status: active
created: 2026-06-02
updated: 2026-06-03
---
Fux is a new sibling tool (beside wagner/bach/orff), implemented 2026-06-02 at
`~/my_programs/fux` (remote `git@github.com:arpitarya/fux.git`, committed locally,
not yet pushed). It is a portable, Claude-aware **knowledge engine**: one
frontmatter substrate in a project's `.fux/` → derived INDEX + graph + memory
views, with $0 deterministic maintenance (Python stdlib only, no third-party deps).

Per the design (`anton/docs/fux-plan.md`, mirrored in `fux/docs/`), Fux is meant
to **replace** three things Anton runs separately — graphify (`graphify-out/`),
cross-session memory (this dir), and the narrative docs (WHAT/WHY/HOW +
architecture) — and add the business-rules layer none held. The plan's rollout
phase 4 is a pilot: `fux init` inside Anton, extracting real rules from
`aggregator.py` (day-pnl, inr-normalization, valuation). Not yet done.

**Why:** future Anton sessions may be asked to adopt Fux or migrate the existing
stores into it.
**How to apply:** if asked to "set up fux here" / migrate graphify or memory,
the engine + `/fux` skill live in the fux repo; run `fux init` in Anton. See
[[project-broker-prime]] and [[project-wagner-dante]] for adjacent context.
