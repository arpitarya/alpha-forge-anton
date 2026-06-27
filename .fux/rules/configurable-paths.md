---
id: configurable-paths
domain: security
type: convention
status: active
tier: constitutional
created: 2026-06-27
updated: 2026-06-27
keywords:
  - path
  - paths
  - env
  - config
  - ANTON_DATA_DIR
  - data-dir
  - configurable
  - filesystem
  - relocatable
code_refs:
  - backend/app/core/paths.py
  - backend/app/modules/brokers/dump_utils.py
  - backend/app/modules/signals/cache_utils.py
  - backend/app/modules/edges/trial_ledger.py
  - backend/app/core/deps.py
related:
  - knowledge-location
  - plan-store
  - no-secrets-in-vcs
  - dump-utils-single-source
seal: 84b9c043a9e4320d
ratification:
  by: arpit arya
  date: 2026-06-27
  content_seal: 0a12fea72d225e00
---
# Configurable paths — no hardcoded filesystem path; one env-driven base

**Constitutional:** No module may hardcode a home-directory or absolute
filesystem path for any directory or file the app reads or writes. Every such
path resolves through the single source of truth `app.core.paths`, derives from
one per-machine base — `ANTON_DATA_DIR` (default `~/.alphaforge-anton`) — and
stays individually overridable by its own documented env var.

Three binding obligations:

1. **One base, one helper.** `app.core.paths.data_dir()` reads `ANTON_DATA_DIR`
   (`~` expanded); `paths.resolve(ENV_VAR, *suffix)` returns the override when
   set (absolute/`~` as-is, relative under the base) else `data_dir()/suffix`.
   New paths call the helper — never `Path.home()`, `~/.alphaforge-anton/...`,
   or a bare absolute literal inline.
2. **Every path is in `.env`.** Each configurable path appears, commented with
   its default, in the tracked `.env` "Filesystem paths" section. The env var is
   the contract; the default is documentation. Real per-machine values → `.env.local`.
3. **Defaults are behaviour-neutral.** When every override is unset the resolved
   paths must equal the pre-existing `~/.alphaforge-anton/...` layout, so an
   existing checkout is unchanged until the operator opts to relocate.

Documented exceptions (not under the base, by design): `BROKER_CACHE_DIR`
(repo-relative `.cache/brokers`), `CLAUDE_PROJECTS` (`~/.claude/projects` — not
Anton's data), `ELGAR_BIN` (an executable, not a path the app writes). The
elgar **store** itself is `paths.elgar_dir()` (`ELGAR_DIR`), and stays
constitutionally outside this repo per [[plan-store]].

**Why:** A hardcoded path is an invisible machine assumption — it breaks on a
fresh clone, a second user, a container, or a relocated disk, and it makes tests
silently touch real home-dir state. Scattering the same `~/.alphaforge-anton`
literal across a dozen modules means a relocation is a dozen-file edit that
*will* miss one. Funnelling every path through one env-driven base makes the app
relocatable by construction and gives the constitution a single enforcement
point: a new hardcoded path is a one-line review catch, not an archaeology dig.
This is a sibling discipline to [[knowledge-location]] (knowledge lives in
exactly one of two git-owned places) and [[no-secrets-in-vcs]] — locations are
declared, never assumed.

**How to apply:**
- New dir/file the app reads or writes → `paths.resolve("MY_THING_DIR", "sub", "dir")`
  (or `paths.data_dir()` / `paths.elgar_dir()`); add the commented default to
  `.env`'s Filesystem-paths section in the same change.
- Never reintroduce `Path.home()`, a `~/.alphaforge-anton/...` string, or an
  absolute path literal in module code. A docstring example (e.g. a manual
  Chrome-launch command) is not a path the app resolves and is out of scope.
- Enforcement: `app.core.paths` is the only place the base literal lives; a
  `grep` for `.alphaforge-anton` / `Path.home()` over `backend/app` (excluding
  `paths.py` and tests) must return only docstrings — wire it into `fux gate`
  alongside the [[plan-store]] checks before relying on it as a wall.
