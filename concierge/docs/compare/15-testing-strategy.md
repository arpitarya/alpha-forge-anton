# 15 — Testing Strategy & Notebooks

## Recommended vs Chosen

| | Choice | Cost |
|---|---|---|
| **Recommended** | Per-file unit test + per-file Jupyter notebook. Fakes for the LLMGateway, NewsAggregator, DB session. | Free |
| **Chosen** | **Same as recommended.** Every new concierge file ships with a paired test and notebook. Tests use SQLite in-memory or transaction-rollback fixtures, fake gateway, fake aggregator. Notebooks are runnable top-to-bottom. | Free |

---

## Context

The user wants individual modules to be testable in isolation, and wants notebooks alongside tests. The [news/](../../news/) package already follows this pattern ([news/tests/](../../news/tests/) + [news/notebooks/](../../news/notebooks/)) — extend the same discipline to concierge.

## Why both tests AND notebooks

Different jobs:

| | Unit tests | Notebooks |
|---|---|---|
| **Audience** | Code (CI) | Humans (debugging, exploration) |
| **Frequency** | Every commit, automatically | When investigating, ad hoc |
| **Output** | Pass/fail | Rendered cells: tables, plots, prompts |
| **Mutability** | Stable, asserted | Free-form, exploratory |
| **Catches** | Regressions, contract violations | "Does this prompt look reasonable?" |
| **Replaces** | Manual verification | Documentation + design playground |

A test asserts that `format_holdings([...])` produces a specific string. A notebook lets you eyeball the actual rendered table and ask "is this what I'd want the LLM to see?" Both matter.

## Layout

```
backend/tests/concierge/
├── conftest.py                    ← shared fixtures
├── test_memory_service.py
├── test_long_term_memory.py
├── test_intent_doc_loader.py
├── test_holdings_service.py
├── test_prompt_builder.py
├── test_intent_router.py
├── test_concierge_service_integration.py
└── fakes/
    ├── fake_gateway.py            ← async iterator returning canned tokens
    ├── fake_aggregator.py         ← returns fixed list[NewsItem]
    ├── fake_holdings_service.py
    └── fake_intent_doc_loader.py

concierge/notebooks/
├── 00_overview.ipynb              ← read-this-first: glossary, sample data
├── 01_memory_service.ipynb
├── 02_long_term_memory.ipynb
├── 03_intent_doc.ipynb
├── 04_holdings.ipynb
├── 05_prompt_builder.ipynb
├── 06_intent_router.ipynb
├── 07_aggregator_query.ipynb
└── 08_end_to_end.ipynb
```

## Testability rules

### 1. Dependency injection at the function boundary

```python
async def stream_concierge(
    request: ConciergeRequest,
    user: UserClaims,
    *,
    db_session: AsyncSession,
    aggregator: NewsAggregator,
    gateway: LLMGateway,
    intent_doc_loader: IntentDocLoader,
    holdings_service: HoldingsService,
    long_term_memory: LongTermMemoryService,
) -> AsyncIterator[bytes]: ...
```

FastAPI wires the real implementations via `Depends`. Tests pass fakes. Nothing is module-global.

### 2. Pure functions wherever possible

Formatters take dicts/lists and return strings:

```python
def format_holdings_snapshot(holdings: list[Holding], as_of: datetime) -> str: ...
def format_news_block(items: list[NewsItem]) -> str: ...
def format_facts_block(facts: list[UserFact]) -> str: ...
def assemble_messages(blocks: PromptBlocks, user_msg: str) -> list[Message]: ...
```

These are trivially unit-testable with no I/O at all.

### 3. DB tests use isolated transactions

```python
@pytest.fixture
async def db_session(test_engine):
    async with test_engine.begin() as conn:
        async with AsyncSession(conn) as session:
            yield session
            await session.rollback()
```

Each test starts with a clean DB state. No tests touch the dev or production database.

### 4. Fakes implement the same protocol as the real thing

```python
class FakeGateway:
    def __init__(self, canned_tokens: list[str]):
        self._tokens = canned_tokens

    async def stream(self, model, messages, **kwargs):
        for tok in self._tokens:
            yield TokenDelta(text=tok)
        yield StreamEnd(usage={"input_tokens": 100, "output_tokens": len(self._tokens)})
```

The real `LLMGateway.stream(...)` signature matches. Tests never network.

### 5. Snapshot tests for prompt assembly

```python
def test_prompt_blocks_for_news_query(snapshot):
    blocks = build_prompt(
        system=SAMPLE_SYSTEM,
        intent_doc=SAMPLE_INTENT,
        facts=SAMPLE_FACTS,
        cross_session_summary=SAMPLE_CROSS_SUM,
        holdings=SAMPLE_HOLDINGS,
        news=SAMPLE_NEWS,
        history=SAMPLE_HISTORY,
        user_msg="What happened with Adani today?",
    )
    snapshot.assert_match(json.dumps(blocks, indent=2), "news_query_prompt.json")
```

Catches accidental block reordering, silently dropped blocks, format regressions. Snapshots reviewed in PR diffs.

### 6. Integration test for the full flow

`test_concierge_service_integration.py` wires real DB (transactional) + fake everything else, runs `stream_concierge` end-to-end, asserts:

- Session created
- History loaded
- News fetched
- Prompt assembled with all blocks
- Tokens streamed
- Both turns persisted
- Meta frame emitted

## Notebook conventions

### Structure (every notebook)

```
1. Setup
   - Imports
   - Fake data factories
   - Service instantiation (with fakes where appropriate)

2. Walkthrough
   - Show inputs
   - Call the function
   - Display outputs with display(Markdown(...)) or pandas

3. Edge cases
   - Empty inputs
   - Maximum-size inputs
   - Error paths

4. Notes
   - Open questions, observations, things to follow up
```

### Notebook-specific tips

- **Use `display(Markdown(...))` to render LLM prompts** — markdown rendering shows headers, tables, code as the LLM will see them.
- **Use `pandas.DataFrame` for token-count breakdowns** per prompt block — makes the cost story visual.
- **Use `await`** at top level (Jupyter 7+ supports it natively for async).
- **Persist sample data in a fixtures file** (`concierge/notebooks/_fixtures.py`) so notebooks and tests share the same examples.
- **Never connect to the real LLM in a notebook by default** — use the fake gateway. Have a clearly marked "Live call" cell at the bottom for ad-hoc real provider calls.

### What each notebook proves

| Notebook | Demonstrates |
|---|---|
| 01 memory | sessions persist; history loads in order; rolling summary kicks in |
| 02 long-term | fact extraction on sample turns; cross-session summary regen |
| 03 intent | profile.md → injected string; mtime cache hit/miss timing |
| 04 holdings | snapshot rendering; cache invalidation; refresh-on-trigger |
| 05 prompt builder | full 8-block prompt; token budget breakdown |
| 06 intent router | routing decisions over a corpus of past queries |
| 07 aggregator | direct NewsAggregator call; per-source contributions; dedup behavior |
| 08 end-to-end | full stream_concierge with fakes; SSE frames; persisted turns |

## CI integration

- Unit tests run on every PR (pytest).
- Notebooks are **not** executed in CI by default — they're for humans. Add a `nbmake` smoke run later if notebook rot becomes a problem.
- Snapshot tests fail loudly on diff; reviewers explicitly approve snapshot updates.

## Coverage targets

- **80% line coverage** on `modules/concierge/*.py` for v1.
- **100% coverage** on the pure formatters (`format_holdings`, `format_news`, etc.) — they're trivial to test fully.
- **No coverage requirement** for `concierge_service.py`'s wiring code — covered by the integration test.

## Open questions

- **Should notebooks live next to the code they exercise** (`backend/app/modules/concierge/notebooks/`) **or under the top-level concierge dir** (`concierge/notebooks/`)? Prefer the top-level concierge dir — keeps the backend module tree clean and matches the news package convention.
- **Snapshot test bitrot**: when prompts evolve, every snapshot must be re-blessed. Acceptable churn during v1; tighten review process once stable.
- **Property-based tests for the formatters** (using `hypothesis`)? Worth it for the token-budget truncation logic — random-size inputs would catch off-by-one bugs in budget enforcement.
- **Notebook output bloat in git**: clear outputs before commit, or use `nbstripout` as a pre-commit hook.
- **Performance regression tests**: capture baseline timings in notebook 08; flag if a change increases mean turn latency by >20%.
