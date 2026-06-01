# Comparison Documents — How to Write Them

How to write a `<name>.compare.md` — the standard format for any "A vs B" decision in
AlphaForge Anton (brokers, libraries, data stores, API providers, UI approaches, model choices).
A comparison doc exists to **land a decision and record why**, so a future reader (human or agent)
never has to re-run the analysis.

## When to write one

Write a `<name>.compare.md` whenever you evaluate two or more interchangeable options and the
choice has lasting consequences. Examples:

- Picking a library or framework (`polars-vs-pandas.compare.md`)
- Choosing a data store or service (`redis-vs-valkey.compare.md`)
- Selecting an LLM / API provider (`gpt-vs-claude-stt.compare.md`)
- Deciding between two implementation approaches (`websocket-vs-sse.compare.md`)

Skip it for trivial or easily reversible choices — a one-line note in the relevant doc is enough.

## File naming & location

- **Name:** `<name>.compare.md`, where `<name>` is the kebab-case subject of the comparison.
  Prefer the `a-vs-b` form when there are exactly two options (`uv-vs-poetry.compare.md`).
- **Location:** `docs/` for cross-cutting decisions; alongside the relevant module
  (e.g. `backend/app/modules/<domain>/`) when the decision is local to that area.
- One decision per file. Don't bundle unrelated comparisons.

## Required structure (verdict first)

Every comparison doc **must** open with the verdict — before context, before the matrix, before
anything else. A reader should learn the answer in the first five seconds; the rest is the
justification they read only if they doubt it.

Required sections, in order:

1. **Verdict** (top of file) — the chosen option, a one-line rationale, confidence, and date.
2. **Context** — what is being compared and why the decision came up.
3. **Options** — the candidates, one short paragraph each.
4. **Comparison matrix** — a table scoring each option against weighted criteria.
5. **Analysis** — per-option pros/cons that the matrix can't capture.
6. **References** — every source the verdict relies on (see rules below).
7. **Additional things to look into** — open questions, risks, and revisit triggers.

## Template (copy this)

```markdown
# <Subject> — Comparison

> **Verdict:** <Chosen option> — <one-line reason>.
> **Confidence:** High | Medium | Low · **Decided:** YYYY-MM-DD · **By:** <name/agent>
> **Revisit when:** <condition that would change this, e.g. "Polars adds X" / "before v2">

## Context

What problem prompted this comparison, the constraints (perf, cost, license, team skill),
and what "winning" means here.

## Options

- **Option A** — one-line description.
- **Option B** — one-line description.

## Comparison matrix

| Criterion (weight) | Option A | Option B |
|--------------------|----------|----------|
| Performance (H)    | …        | …        |
| Ergonomics (M)     | …        | …        |
| Ecosystem (M)      | …        | …        |
| License / cost (H) | …        | …        |
| Maintenance risk (L)| …       | …        |
| **Score**          | …        | …        |

Use H/M/L weights and keep cells terse — claims, not paragraphs. Back every non-obvious cell
with a reference.

## Analysis

### Option A
- **Pros:** …
- **Cons:** …

### Option B
- **Pros:** …
- **Cons:** …

## References

- [Official docs — feature X](https://…) — confirms perf claim in matrix
- [Benchmark / issue / PR](https://…) — accessed YYYY-MM-DD
- Internal: [docs/architecture.md](architecture.md) — current usage

## Additional things to look into

- Open question that wasn't resolved here.
- Known risk or assumption that could invalidate the verdict.
- What to re-measure before the next major version / revisit date.
```

## Section rules

- **Verdict** — state the decision, not the deliberation. If you can't commit, say "Lean A,
  pending <X>" and add X to *Additional things to look into*. Always include the date so staleness
  is visible.
- **Comparison matrix** — pick criteria *before* scoring to avoid bias toward a favourite. Mark
  weights (H/M/L). A tie in the matrix means the verdict rests on the weighted, not raw, count —
  make that reasoning explicit in the Analysis.
- **References** — non-negotiable. Every factual claim (a benchmark number, a license term, a
  missing feature) needs a source. Use real links, note the **access date** for anything that can
  change (benchmarks, pricing, roadmaps), and prefer primary sources (official docs, source code,
  release notes) over blog posts. Cite internal docs/code with repo-relative links.
- **Additional things to look into** — capture what you deliberately did *not* test, assumptions
  you couldn't verify, and the concrete trigger that should reopen the decision. This is what keeps
  the doc honest as the world changes.

## Checklist before committing

- [ ] File named `<name>.compare.md`, kebab-case subject
- [ ] **Verdict is the first content in the file** (chosen option + reason + confidence + date)
- [ ] Comparison matrix with weighted criteria and a score row
- [ ] Every non-obvious claim has a reference; volatile sources have access dates
- [ ] *Additional things to look into* lists open questions and a revisit trigger
- [ ] Linked from the relevant doc index if it's a cross-cutting decision

## Example skeleton

```markdown
# uv vs Poetry — Comparison

> **Verdict:** uv — 10–100× faster installs, single static binary, drop-in for our CI.
> **Confidence:** High · **Decided:** 2026-06-01 · **By:** arpit

## Context
We need one Python package/dependency manager for a Python 3.14 monorepo backend…
```

See [docs/conventions.md](conventions.md) for general documentation style and the
"every code change ships with a doc update" rule.
