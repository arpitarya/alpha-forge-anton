# Debate — `elgar-mandate` → constitutional (proposed)

**Proposed rule:** "Elgar is the suite's private money store: every money document and
hard PII lives only in Elgar's private git repo (0700, one commit per save), public repos
hold only `elgar://plan/<id>` links; home decided by the two-place test. Boundary enforced
by [[plan-store]]."
**Tier sought:** constitutional (apex — always-blocking, sealed)
**Date:** 2026-06-28
**Format:** two-agent free debate (anti-sycophancy). Both agents briefed identically,
side-free, blind to each other's first pass. Human is tie-breaker + ratifier.

---

## Blind first pass — Agent A

**Position: REJECT** (fold into `plan-store` as a non-constitutional amendment).

The proposed rule re-states invariants already sealed: `plan-store` (constitutional, ratified
2026-06-17) already binds "this repo holds `elgar://plan/<id>` links, never content"; the
two-place test is already owned by `knowledge-location`. Elgar's README itself says elgar "is
one half of the two-place rule (Anton's `knowledge-location`)" — elgar is the *implementation*,
not a new charter.

Apply the test. Prong one (wrong answer costs money/PII): yes. Prong two requires a *distinct*
invariant that never changes — `elgar-mandate` adds none. The genuinely new material (0700,
ELGAR_DIR-overridable, one-commit-per-save) is **mechanism, not invariant**, and per
`store.py:53-61,81-92` that mechanism *already drifted*: the store is a **subdirectory of the
elgar source repo sharing one `.git`** (pathspec-scoped commits), not "its own private repo
outside any public tree" as the wording and README claim.

**Objection:** redundant apex clutter that imports a falsifiable claim. (a) Duplication with
*weaker* enforcement — `plan-store` is gated by `dante pii` + `fux gate`; the extra clauses
(0700, one-commit) have **no gate** in anton's CI → half-unenforced theater, the exact defect
the prior plan-store debate spent two rounds purging. (b) The two-place test is guidance, not a
deterministic gate — sealing a non-deterministic test at the apex repeats "a constitution its
tooling can't honour." And "private repo outside any public tree" is **factually false** against
`store.py`'s shared `.git`.

**Amended:** don't adopt as a separate constitutional rule. Add one mechanism sentence to
`plan-store`; file the 0700/one-commit/two-place heuristic as a `standard` rule; fix the
store.py/README contradiction first.

## Blind first pass — Agent B

**Position: REJECT** as a separate constitutional rule; fold the one novel enforceable clause
into `plan-store`.

`plan-store` (sealed `content_seal: e43f9a09…`) already nails the constitutional half — a
prohibition anton's own tooling can block. `elgar-mandate` re-states it and adds an *affirmative
charter*: elgar *must* be 0700, *must* be one-commit-per-save, *must* be ELGAR_DIR-overridable.
Those live in `store.py` (`init()` chmod 0700, `save()` one `_commit`, `root()` honours
ELGAR_DIR) — **not anton's to enforce**. Nothing in anton runs when someone edits `store.py` to
chmod 0755 or batch-commits. The affirmative half is aspiration at the apex — the "theater" the
original debate purged from plan-store.

**Objection:** the charter's own example contradicts the shipped code. README + rule say "private
git repo outside any public work tree, mode 0700," but `store.py:17-18,53-57,83-85` are explicit:
the store is a subdirectory of the elgar source repo; the `.git` (and thus plan blobs/history)
lives at `_REPO_ROOT`, not under the 0700 dir. If elgar's source repo were pushed public, the
0700 bit is irrelevant — the blobs are in history. The charter constitutionalizes a guarantee the
implementation does not provide, and anton cannot detect the violation. Worse, "one commit per
save → history/diff/rollback" *can legitimately change* (SQLite, squash) — failing prong two.

**Amended:** not a separate constitutional rule. (a) Add a placement-test sentence to `plan-store`
(governs anton's own placement choices). (b) Put elgar's affirmative obligations as a `standard`
rule **in elgar's own `.fux/`**, where its CI can `stat` the dir and assert commit-per-save —
after fixing store.py/docs so "outside any public tree" is true or dropping the phrase.

---

## Adversarial round (host)

Both agents converged blind on REJECT, and both independently surfaced the same factual bug.
I verified it directly against source: `store.py` line 17 `DEFAULT_ROOT = parents[2]/"store"`,
line 18 `_REPO_ROOT = parents[2]`, line 49 commits run `cwd=_REPO_ROOT`, lines 54 & 83-85 state
in-code that "the store shares its git repo with the elgar source." The default store is inside
the elgar repo (a committed `store/` dir exists there). The "outside any public tree" claim is
false for the default root. Convergence survives falsification.

## Converged outcome

**Do not ratify `elgar-mandate` as constitutional.** The boundary is *already* constitutional
(`plan-store`) and the two-place test is *already* owned (`knowledge-location`). The honest forms:
1. Optionally add one mechanism/placement sentence to `plan-store` (narrows mechanism; the prior
   debate noted such a narrowing needs no re-seal — confirm before relying on that).
2. File elgar's affirmative obligations (0700, ELGAR_DIR, one-commit-per-save) as a `standard`
   rule **in a new `elgar/.fux/`**, where elgar's own CI can test them.
3. **Fix first:** reconcile README/charter "private repo outside any public tree" with
   `store.py`'s shared-`.git` reality before sealing that phrase anywhere.

## Residual risk

- Leaving elgar's positive obligations ungoverned until its own `.fux/` exists. Mitigation: the
  *leak* surface (the part that costs PII) is already gated by `plan-store`; what remains
  ungoverned is internal hygiene (dir mode, commit granularity), lower blast radius.

---

## Amendment — 2026-06-28: merge of `anton-delegates-elgar-store`

The standard ADR `anton-delegates-elgar-store` (Anton owns no elgar filesystem path;
all elgar I/O goes through the elgar CLI API; fail-loud; `ELGAR_DIR` is elgar-side,
not Anton; deliberate exception to `configurable-paths`) was folded into this
constitutional rule at the human ratifier's direction — its decision, consequences,
and `code_refs` now live in `elgar-mandate`, and the standalone ADR was removed.
The rule was re-ratified (`fux ratify elgar-mandate`) to re-stamp `content_seal`
over the amended body. No other rule linked the ADR, so no inbound links broke.
