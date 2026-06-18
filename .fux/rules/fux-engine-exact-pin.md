---
id: fux-engine-exact-pin
domain: process
type: convention
status: active
created: 2026-06-19
updated: 2026-06-19
code_refs:
  - pyproject.toml
  - uv.lock
related: [project-fux, doc-per-code-change]
aliases: [fux-version-pin]
keywords: [fux-engine, dependency, pin, uv, lockfile, version]
---
**Convention:** `fux-engine` is exact-pinned in the root `pyproject.toml`
(`fux-engine==<version>`, not a floor like `>=`), and `uv.lock` is kept in sync
via `uv lock` after every bump. This repo always runs one known-exact fux-engine
version — never "whatever satisfies the floor."

**Why:** the project root has a separate global pyenv install of `fux-engine`
(an editable clone of `~/my_programs/fux`, used for the `fux` CLI) that can
drift independently of what `uv sync` puts in Anton's `.venv` — that drift
already happened once (CLI at 0.6.0, workspace locked at 0.4.0 via a `>=0.4.0`
floor that PyPI resolved to the oldest match). An exact pin removes the
ambiguity: the workspace dependency and the lockfile always name the same
version, and a version bump is a deliberate, visible diff.

**How to apply:** to upgrade, edit the pin in `pyproject.toml` to the new exact
version, then run `uv lock && uv sync`. Never widen back to a floor (`>=`) or
range. See [[project-fux]] for the two separate install paths (pyenv global CLI
vs. uv workspace) that make this matter.
