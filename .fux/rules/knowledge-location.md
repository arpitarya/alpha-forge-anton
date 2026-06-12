---
id: knowledge-location
domain: security
type: convention
status: active
created: 2026-06-12
updated: 2026-06-12
related: [plan-store, no-secrets-in-vcs, doc-per-code-change]
aliases: [two-place-rule, no-home-dir-knowledge, pack-policy]
keywords: [knowledge, location, pack, elgar, fux, home-directory]
---
**Convention:** every authored knowledge document lives in exactly one of two
version-controlled places — never anywhere else, including `~/.claude/fux/packs/`:

1. **This repo's `.fux/`** — anything public-safe: conventions, formulas,
   regulatory facts, investment principles (percentages and statutes, no
   personal figures). Includes the Indian tax/market rules formerly in the
   `indian-markets-tax` home-dir pack (moved here 2026-06-12; `packs = []` in
   `config.toml`).
2. **The elgar store** (`~/.alphaforge-anton/elgar`, its own private git repo)
   — anything with personal figures: plans, targets, corpus, SIP amounts.
   Fux holds only `elgar://plan/<id>` links ([[plan-store]]).

The only exception is `~/.claude/fux/global/` — those four engine defaults are
seeded from the fux package's own git repo, so they are versioned tool code,
not loose documents. `use_global = true` stays.

**Why:** a home-directory pack is invisible knowledge — not in any git history,
not backed up with a repo, not on a fresh machine after a clone, and silently
divergent from the repo that depends on it. Both allowed places are git repos
with a clear owner and a clear privacy level; the split between them is decided
by content ([[plan-store]]: does it change with *my money* or with the world/
the code), never by convenience.

**How to apply:** when authoring a new entry, choose by privacy: public-safe →
`.fux/rules/` here; personal → elgar. Never create or opt into a home-dir pack
(`packs` in `config.toml` stays empty). If knowledge must be shared with a
future second project, copy the entry into that project's `.fux/` — duplication
in two git repos beats a shared mutable location in zero.
