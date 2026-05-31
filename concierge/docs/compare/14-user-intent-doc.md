# 14 — User Intent Document

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | A markdown file the user authors, loaded with mtime-based caching, injected as a system block | Free |
| **Chosen** | **Markdown file at `concierge/intent/profile.md` (gitignored), template at `profile.template.md` (committed). Loaded by `concierge_intent_doc_loader.py` with file-mtime caching. Injected as prompt block 2.** | Free |

---

## Context

The user wants a "core document where I can describe what I want" — a place to declare investment philosophy, risk tolerance, sector preferences, exclusions, goals, and style preferences for how Orff should respond. This document gets injected into every conversation so Orff is always aligned.

This is different from extracted facts (which Orff infers from conversations — see [12](12-long-term-memory.md)). The intent document is **explicit, user-authored, durable**, and **always present**.

## Options

### A. Markdown file in the repo

User edits `concierge/intent/profile.md` with any text editor (VSCode, vim, Notes). Backend reads on every turn, caching by file mtime so unchanged files are zero-cost.

### B. DB-backed editable text field

`concierge_user_profile` table with an `intent_document text` column. UI surfaces it as a `<textarea>` the user edits in-app.

### C. Structured form (typed fields)

UI form with fields: risk tolerance dropdown, time horizon slider, sector preferences multi-select, exclusions free-text list. Saved as JSON. Rendered into a templated markdown block for the LLM.

### D. Hybrid: typed core + free-text appendix

Combines C and A. Structured fields for things with clear taxonomies (risk tolerance: low/medium/high), free-text markdown for everything else.

## Comparison

| Dimension | A. File | B. DB textarea | C. Typed form | D. Hybrid |
|---|---|---|---|---|
| Setup cost | Trivial (one file loader) | Medium (UI + endpoint + table) | High (form UI + schema + renderer) | High (both) |
| Editing experience | User's favorite editor | In-app textarea | Form fields | Mixed |
| Versioning | User's git or editor | DB has no history unless added | DB has no history unless added | DB has no history |
| Expressiveness | Full markdown, no schema constraints | Same as A | Constrained to known fields | Constrained + open |
| Multi-user friendly | No (single file path) | Yes (per-user row) | Yes (per-user row) | Yes |
| Self-hosted friendly | Excellent (file is local) | Fine | Fine | Fine |
| LLM injection cost | ~500–1500 tok | Same | Smaller (~300 tok if compact) | ~500–1500 tok |
| Survives DB wipes | Yes (in filesystem) | No | No | No |

## Tradeoffs

- **A. File** — best fit for Anton's design (single-tenant, self-hosted, power user). The file lives in the user's filesystem, owned by them, edited with their tools, backed up however they back up their filesystem. No UI work. Doesn't constrain expressiveness — the user can write whatever they think Orff should know.
- **B. DB textarea** — adds a UI to recreate what a text editor already does, without giving the user any new capability. Worth it only when Anton goes multi-user and per-user DB rows become necessary.
- **C. Typed form** — over-engineered for a single user. Forces decisions ("low/medium/high risk tolerance") that don't capture the real shape of investor preferences. Constraining the schema means the user can't express things the schema didn't anticipate.
- **D. Hybrid** — combines the costs of B and C without solving anything A doesn't already solve for a single user.

## Recommendation

**A. Markdown file at `concierge/intent/profile.md` with a committed template.**

### File layout

```
concierge/intent/
├── README.md                 ← committed, explains how to use
├── profile.template.md       ← committed, sample content to copy
├── profile.md                ← gitignored, user's actual file
└── archive/                  ← gitignored, optional snapshots
```

### `.gitignore` addition

```
concierge/intent/profile.md
concierge/intent/archive/
```

### Template content

See [§13 of the architecture doc](../4-news-llm-architecture.md#13-user-intent-document) for the full template.

### Loader behavior

```python
class IntentDocLoader:
    def __init__(self, path: Path):
        self._path = path
        self._cached_text: str = ""
        self._cached_mtime: float = 0.0

    def load(self) -> str:
        if not self._path.exists():
            return ""
        mtime = self._path.stat().st_mtime
        if mtime != self._cached_mtime:
            self._cached_text = self._path.read_text(encoding="utf-8")
            self._cached_mtime = mtime
        return self._cached_text
```

- Hot-reload via mtime: editing the file → next turn picks it up. No restart needed.
- Empty if file missing: cold-start users get a working (if less personalized) experience.
- Wrapped in `<user_intent>...</user_intent>` tags when injected so the LLM clearly distinguishes user-authored guidance from system rules.

### Prompt injection

```
<user_intent>
{contents of profile.md}
</user_intent>

Honor the user's stated philosophy, risk tolerance, exclusions, and style
preferences above. When their stated goals conflict with optimal returns,
default to their stated preferences but flag the tradeoff.
```

### Path resolution

- Configurable via `CONCIERGE_INTENT_DOC_PATH` env var, defaults to `concierge/intent/profile.md` relative to project root.
- For multi-user later: `CONCIERGE_INTENT_DOC_DIR` + `{user_id}.md` per-user files.

## Why a file beats a DB row (for now)

- **You can edit it from anywhere** — IDE, terminal, phone over SSH. No need for the app to be running or for the UI to support what your text editor already does well.
- **Markdown is the right format** — Claude and other LLMs already parse markdown structure; the user's mental model maps directly to what the model sees.
- **No migration headaches** — schema-less, version-able with git, copy/paste-able.
- **Survives DB resets** during development.

## Migration to UI later

When Anton goes multi-user (or when the user wants in-app editing), the loader contract stays the same — swap the file backend for a DB backend behind the same interface:

```python
class DBIntentDocLoader(IntentDocLoader):
    def load(self, user_id: UUID) -> str: ...
```

Zero change to `prompt_builder` or anything downstream.

## Open questions

- **Document size cap**: should we warn if the file exceeds (say) 4k tokens? It would crowd out other context. Soft warning in logs is enough.
- **Validation**: should we lint the file (e.g., make sure section headers exist) or accept any markdown? Accept any markdown — it's the user's voice.
- **Multiple personas**: power user might want different intent docs per investment account (long-term, trading, kids' education fund). Out of scope for v1; could extend to `profile-{persona}.md` with a `?persona=` query param.
- **Template iteration**: as we learn what's most useful in the intent doc, update the committed template. The template is a living document, not a contract.
- **Privacy**: same as holdings — when sending to free LLM providers, the user's intent doc is leaving the machine. Document the privacy boundary in the `intent/README.md`.
