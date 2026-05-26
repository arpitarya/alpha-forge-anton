# Chat + Memory Plan — AlphaForge Anton

## Goal

Upgrade the Alpha chat module to use the **Anthropic API directly** (Claude Sonnet / Haiku)
with **server-side persistent memory** shared by both the chat rail and the future voice interface.

---

## Current State

| Layer | What exists |
|-------|-------------|
| Backend | `chat_routes.py` → `chat_service.py` → `alphaforge_anton_llm.gateway` (multi-provider abstraction). No DB persistence. |
| Frontend | `useChatStream.ts` holds up to 6 turns in React state; cleared on refresh. |
| Voice | `AlphaBar.tsx` has a Voice/Chat toggle but voice is a stub. |

---

## Target Architecture

```
frontend (ChatRail / VoiceRail)
        │  POST /api/v1/chat  { session_id?, messages, model }
        ▼
chat_routes.py
        │
        ▼
chat_service.py  ──► chat_memory_service.py  ──► PostgreSQL
        │                (load + persist turns)    chat_sessions
        │                                          chat_turns
        ▼
Anthropic SDK (anthropic.AsyncAnthropic)
  claude-sonnet-4-6  /  claude-haiku-4-5
        │  SSE streaming (stream_text)
        ▼
StreamingResponse → frontend
```

Both chat and voice will send `session_id` in requests and read from the same `chat_turns` table,
so conversation context is shared across modalities.

---

## Data Model

### `chat_sessions`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `user_id` | UUID FK → wagner users | owner |
| `title` | varchar(120) | auto-generated from first message |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

### `chat_turns`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `session_id` | UUID FK | |
| `role` | varchar(16) | `user` \| `assistant` |
| `content` | text | |
| `model` | varchar(64) | which Claude model answered |
| `tokens_in` | int | prompt tokens |
| `tokens_out` | int | completion tokens |
| `elapsed_ms` | int | |
| `source` | varchar(16) | `chat` \| `voice` — origin modality |
| `created_at` | timestamptz | |

---

## Backend Changes

### New files

| File | Lines | Purpose |
|------|-------|---------|
| `backend/app/modules/chat/chat_memory_models.py` | ≤ 60 | SQLAlchemy ORM for `chat_sessions` + `chat_turns` |
| `backend/app/modules/chat/chat_memory_service.py` | ≤ 100 | `get_or_create_session`, `load_history`, `append_turn` |
| `backend/alembic/versions/xxxx_chat_memory.py` | — | Alembic migration |

### Modified files

**`chat_schemas.py`** — add:
```python
class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: ModelSlug = "auto"
    session_id: str | None = None   # client passes back what it received
    source: Literal["chat", "voice"] = "chat"
```

Add response envelope:
```python
class ChatStreamMeta(BaseModel):
    session_id: str
    turn_id: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    elapsed_ms: int
```

**`chat_service.py`** — replace `alphaforge_anton_llm.gateway` call with direct Anthropic SDK:
- Import `anthropic.AsyncAnthropic` (add `anthropic` to `backend/pyproject.toml`)
- Use `client.messages.stream(...)` for true token-level SSE
- Load history from `chat_memory_service.load_history(session_id, limit=20)` instead of
  the 6-turn client-supplied window
- After streaming completes, persist both turns via `chat_memory_service.append_turn`
- Keep the `_SYSTEM` prompt and intent-based model routing logic; just swap the provider

**`chat_routes.py`** — inject `AsyncSession` dep, pass to service; return `session_id` in the
first SSE frame so the client can persist it.

### Anthropic model mapping

| ModelSlug | Claude model |
|-----------|-------------|
| `auto` (investment/plan intent) | `claude-sonnet-4-6` |
| `auto` (factoid/fast intent) | `claude-haiku-4-5-20251001` |
| `claude-sdk` (explicit) | `claude-sonnet-4-6` |

Keep other provider slugs routing through the existing gateway unchanged; only `claude-sdk`
and `auto` move to the direct SDK.

### Prompt caching

Wrap the `_SYSTEM` prompt + static portfolio context in an Anthropic cache-control block
(`"cache_control": {"type": "ephemeral"}`) so repeated turns in one session hit the 5-min cache.
This cuts prompt token cost by ~80% for multi-turn sessions.

---

## Frontend Changes

### `useChatStream.ts`

- On first submit: no `session_id` in request body.
- Parse the first SSE frame for `session_id`; store in a `useRef`.
- All subsequent submits in the same component mount include `session_id`.
- On `clear()`, reset `session_id` ref so next submit starts a new session.
- Remove the hard 6-turn client history window — history is now server-authoritative.
  Still send the current turn's user message; backend merges with DB history.

### `chat.types.ts`

- Add `sessionId: string | null` to hook return type.
- Add `source: "chat" | "voice"` to the submit signature (defaults `"chat"`).

### `AlphaBar.tsx` / future `VoiceRail.tsx`

- Voice submit calls `submit(transcript, modelId, "voice")` — same hook, source flag differs.
- Session is shared: voice continues the same conversation thread as chat.

---

## Environment / Config

Add to `.env` and `backend/app/core/config.py`:

```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_DEFAULT_MODEL=claude-sonnet-4-6
ANTHROPIC_FAST_MODEL=claude-haiku-4-5-20251001
```

Add `anthropic>=0.50` to `backend/pyproject.toml` dependencies.

---

## Implementation Order

1. **Alembic migration** — `chat_sessions` + `chat_turns` tables
2. **`chat_memory_models.py`** — ORM models
3. **`chat_memory_service.py`** — load/persist helpers
4. **Update `chat_schemas.py`** — add `session_id`, `source`, `ChatStreamMeta`
5. **Update `chat_service.py`** — swap to Anthropic SDK, wire memory, add prompt caching
6. **Update `chat_routes.py`** — inject DB session, thread through `session_id`
7. **Update `config.py`** — add Anthropic env vars
8. **Update `useChatStream.ts`** — session_id ref, remove client history window
9. **Update `chat.types.ts`** — `sessionId` + `source`
10. **Docs update** — update `architecture.md` AI row and this file

---

## Out of Scope (future)

- Voice STT/TTS integration (will read `chat_turns` with `source = "voice"`)
- Session list / history browser UI
- Multi-session management / session titles
- RAG over portfolio data (future: inject holdings snapshot into system prompt)
