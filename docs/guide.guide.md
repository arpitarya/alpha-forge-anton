# Guides — How to Write Them

How to write a `<name>.guide.md` — the standard format for any "how to produce X
correctly" document in AlphaForge Anton (writing a Fux rule, adding a broker,
authoring a probe, shaping a comparison). A guide exists to **capture a
repeatable practice once**, so a future contributor (human or agent) can produce
a correct artifact without re-deriving the method.

`comparison.guide.md` is itself a `.guide.md` — a guide for writing comparisons.
This file is the pattern every guide follows.

## When to write one

Write a `<name>.guide.md` whenever a task has a *right way* that you'd otherwise
re-explain each time, or whenever you define a new repeatable artifact type.
Examples:

- A new document type (`compare.guide.md`, this file)
- A recurring authoring task (`rule.guide.md` — how to write a Fux rule)
- A multi-step contributor workflow (`broker.guide.md`, `probe.guide.md`)

Skip it for a one-off task, or where a few lines in the relevant doc suffice. A
guide earns its place only when the practice repeats.

## File naming & location

- **Name:** `<name>.guide.md`, where `<name>` is the kebab-case subject (the
  artifact or practice the guide produces).
- **Location:** `docs/` for cross-cutting practices; alongside the relevant
  module (e.g. `backend/app/modules/<domain>/`) when the practice is local.
- One practice per file. Don't bundle unrelated how-tos.

## Required structure (purpose first)

Every guide **must** open with its purpose — what artifact it lets you produce
and when to reach for it. A reader should know in the first five seconds whether
this is the right guide; the rest is the method.

Required sections, in order:

1. **Purpose** (top of file) — what you can produce with this guide, and when to use it.
2. **When to write/use one** — the trigger; and explicitly when to skip.
3. **Naming & location** — if the guide defines an artifact type, where it lives.
4. **The pattern** — the required steps or required sections of the artifact.
5. **Template** — a copy-paste skeleton of the artifact.
6. **Section/step rules** — the non-obvious rules that make the artifact good.
7. **Checklist before committing** — a final pass the author runs.
8. **Example** — a short, real, repo-grounded instance.

## Template (copy this)

```markdown
# <Subject> — How to Write Them   (or: How to <do the practice>)

One-paragraph purpose: what artifact this produces, who reads it, and why the
practice is worth standardizing.

## When to write/use one
The trigger that calls for it — and when to skip it.

## Naming & location        (omit if the guide isn't about an artifact type)
- **Name:** `<name>.<role>.md`, kebab-case subject.
- **Location:** `docs/` for cross-cutting; alongside the module when local.

## The pattern
The required steps or sections, in order, each with a one-line purpose.

## Template (copy this)
\`\`\`markdown
<the copy-paste skeleton of the artifact>
\`\`\`

## Section/step rules
- Rule per section/step: the non-obvious thing that makes it correct.

## Checklist before committing
- [ ] Named correctly
- [ ] <the load-bearing requirement> is present and first
- [ ] <other must-haves>
- [ ] Linked from the relevant doc index if cross-cutting

## Example
A short, real instance — or a link to one in the repo.
```

## Section rules

- **Purpose first** — like a comparison's verdict, the purpose leads. State what
  the reader can *make* with the guide, not the history of why it exists.
- **Be prescriptive** — a guide gives rules, not musings. Prefer "do X" over
  "you might consider X". If something is optional, say so explicitly.
- **Always include a copyable template** — the template is the most-used part of
  any guide. Keep it complete enough to paste and fill in.
- **Ground the example** — use a real artifact from this repo (or a faithful
  skeleton), never a contrived one. Link to it where it lives.
- **End with a checklist** — the checklist is what authors actually run before
  committing; make every item binary and load-bearing.
- **Keep it current** — a guide that drifts from practice is worse than none.
  Per [conventions.md](conventions.md), update the guide in the same session you
  change the practice it documents.

## Checklist before committing

- [ ] File named `<name>.guide.md`, kebab-case subject
- [ ] **Purpose is the first content in the file** (what it produces + when to use it)
- [ ] "When to use" includes an explicit *skip* condition
- [ ] A complete, copy-paste **Template** is present
- [ ] Section/step rules capture the non-obvious requirements
- [ ] Checklist items are binary and load-bearing
- [ ] At least one real, repo-grounded example
- [ ] Linked from the relevant doc index if it's a cross-cutting practice

## Example skeleton

```markdown
# Fux Rules — How to Write Them

Purpose: produce a `.fux/rules/<id>.md` entry that captures one business rule,
links it to the code that implements it, and stays verifiable.

## When to write one
Whenever business logic has a *why* that isn't obvious from the code…

## The pattern
1. Frontmatter — id, domain, type, status, code_refs, related.
2. Body — Rule, Formula, Why, Edge cases.
…
```

See [comparison.guide.md](comparison.guide.md) for a fully worked instance of
this pattern, and [conventions.md](conventions.md) for general documentation
style and the "every code change ships a doc update" rule.
