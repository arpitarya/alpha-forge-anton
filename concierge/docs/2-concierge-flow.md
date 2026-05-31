# Concierge Backend — Flow Diagrams

## 1. End-to-End Request Lifecycle

```mermaid
sequenceDiagram
    actor User
    participant ConciergeRail
    participant Hook as useConciergeStream
    participant Proxy as Next.js Proxy
    participant Routes as concierge_routes
    participant Deps as deps.py
    participant Service as concierge_service
    participant Memory as concierge_memory_service
    participant DB as PostgreSQL
    participant Claude as Anthropic SDK

    User->>ConciergeRail: type message, press Enter
    ConciergeRail->>Hook: onSeed(query)
    Hook->>Hook: append optimistic turn loading=true
    Hook->>Proxy: POST /api/v1/concierge with session_id
    Proxy->>Routes: forward to backend port 8000
    Routes->>Deps: validate JWT
    Deps-->>Routes: UserClaims id + role + email
    Routes->>Service: stream_concierge(messages, model, session_id)

    Service->>Memory: get_or_create_session(session_id, user_id)
    Memory->>DB: SELECT or INSERT concierge_sessions
    DB-->>Memory: session row
    Memory-->>Service: session_id UUID

    Service->>Memory: load_history(session_id, limit=20)
    Memory->>DB: SELECT concierge_turns ORDER BY created_at
    DB-->>Memory: turn rows
    Memory-->>Service: list of Messages

    Service->>Service: resolve model + build messages array
    Service->>Claude: messages.stream with cached system prompt

    loop token streaming
        Claude-->>Service: TextDeltaEvent
        Service-->>Routes: yield SSE delta frame
        Routes-->>Hook: StreamingResponse chunk
        Hook->>Hook: accumulate and patchTurn
        ConciergeRail->>User: render streaming response
    end

    Claude-->>Service: MessageStopEvent with usage
    Service->>Memory: append_turn user then assistant
    Memory->>DB: INSERT two concierge_turns rows
    Service-->>Routes: yield SSE meta frame
    Routes-->>Hook: data DONE
    Hook->>Hook: patchTurn loading=false
```

---

## 2. Backend Module Dependency Graph

```mermaid
flowchart TD
    subgraph Entry["FastAPI App"]
        MAIN["app/main.py"]
        MODULES["app/modules/init.py"]
    end

    subgraph ConciergeModule["concierge module"]
        ROUTES["concierge_routes.py"]
        SERVICE["concierge_service.py"]
        SCHEMAS["concierge_schemas.py"]
        MEM_SVC["concierge_memory_service.py"]
        MEM_MDL["concierge_memory_models.py"]
    end

    subgraph Core["app/core"]
        DEPS["deps.py"]
        CONFIG["config.py"]
        DB["db.py"]
        SEC["security.py"]
    end

    subgraph External["External"]
        ANT["anthropic.AsyncAnthropic"]
        PG[("PostgreSQL")]
    end

    MAIN --> MODULES --> ROUTES
    ROUTES --> DEPS
    ROUTES --> SERVICE
    ROUTES --> SCHEMAS
    SERVICE --> SCHEMAS
    SERVICE --> MEM_SVC
    SERVICE --> CONFIG
    SERVICE --> ANT
    MEM_SVC --> MEM_MDL
    MEM_SVC --> DB
    MEM_MDL --> PG
    DEPS --> SEC
    DB --> PG
```

---

## 3. Memory Service Internal Flow

```mermaid
flowchart TD
    A(["stream_concierge called\nsession_id: str or None"]) --> B{"session_id provided?"}

    B -- No --> C["INSERT concierge_sessions\nid=uuid4, user_id, title"]
    B -- Yes --> D["SELECT concierge_sessions\nWHERE id=session_id\nAND user_id=caller"]
    D --> E{"row found?"}
    E -- No or wrong owner --> F["raise 404 or 403"]
    E -- Yes --> G["return session_id"]
    C --> G

    G --> H["load_history\nSELECT concierge_turns\nORDER BY created_at\nLIMIT 20"]
    H --> I["map rows to list of Message"]
    I --> J(["return history to concierge_service"])

    J --> K["build messages array\n1. system prompt cached\n2. history turns\n3. new user message"]
    K --> L["Anthropic stream completes"]

    L --> M["INSERT concierge_turns\nrole=user, source=concierge or voice"]
    M --> N["INSERT concierge_turns\nrole=assistant, model\ntokens_in, tokens_out, elapsed_ms"]
    N --> O(["done"])
```

---

## 4. Anthropic SDK Streaming to SSE Chain

```mermaid
sequenceDiagram
    participant Service as concierge_service
    participant SDK as Anthropic SDK
    participant Route as concierge_routes
    participant Hook as useConciergeStream

    Service->>SDK: messages.stream(model, system with cache, messages)
    SDK-->>Service: stream_start

    Service-->>Route: yield first SSE frame with session_id

    loop per token
        SDK-->>Service: text_delta event
        Service-->>Route: yield SSE delta frame
        Route-->>Hook: StreamingResponse bytes
        Hook->>Hook: accumulate and patchTurn response
    end

    SDK-->>Service: message_stop with usage
    Service->>Service: persist both turns to DB
    Service-->>Route: yield SSE meta frame elapsed and tokens
    Route-->>Hook: data DONE
    Hook->>Hook: patchTurn loading=false
```

---

## 5. Frontend Component Tree

```mermaid
flowchart TD
    subgraph Layout["layout.tsx root"]
        TP[ThemeProvider]
        QP[QueryProvider]
        AG[AuthGuard]
        BG[BootGate]
        CP[ConciergeProvider]
    end

    CP --> US["useConciergeStream\nturns, sessionRef, open\nsubmit, clear"]
    CP --> AB["AlphaBar.tsx\nVoice or Concierge toggle + Deploy"]
    CP --> CR["ConciergeRail.tsx\nthread + composer\nResponseBody markdown"]

    US -->|turns + open| CR
    US -->|submit| AB
    US -->|submit| CR

    CR --> MP["ModelPicker.tsx\nauto, claude-sdk, gemini, groq"]

    subgraph Future["future - Voice"]
        VR["VoiceRail.tsx\nSTT transcript"]
        TTS["TTS playback"]
        VR -->|submit source=voice| US
        US -->|response text| TTS
    end
```

---

## 6. Prompt Caching Strategy

```mermaid
flowchart LR
    subgraph Payload["messages payload to Anthropic"]
        SYS["system block\ncontent: _SYSTEM ~500 tokens\ncache_control: ephemeral\nTTL 5 min"]
        CTX["context block optional\nportfolio snapshot\ncache_control: ephemeral\nper-session TTL"]
        HIST["history messages\nup to 20 turns from DB\nno cache_control\ndynamic each request"]
        CUR["current user message\nnew, no cache_control"]
    end

    SYS --> A["~80% cache hit rate\non system prompt"]
    CTX --> B["per-session cache\nif portfolio injected"]
    HIST --> C["always billed\ndynamic content"]
    CUR --> C
```

---

## 7. Model Routing Decision Tree

```mermaid
flowchart TD
    A(["request arrives\nmodel: ModelSlug"]) --> B{"model == auto?"}

    B -- Yes --> C{"regex match\non user message"}
    C -- investment intent --> D["QueryType.INVESTMENT_PLAN\nclaude-sonnet-4-6"]
    C -- factoid intent --> E["QueryType.FACTOID\nclaude-haiku-4-5"]
    C -- news intent --> F["QueryType.NEWS_LOOKUP\nclaude-haiku-4-5"]
    C -- portfolio intent --> G["QueryType.PORTFOLIO_OVERVIEW\nclaude-sonnet-4-6"]
    C -- no match --> H["QueryType.MULTI_TURN\nclaude-sonnet-4-6"]

    B -- No --> I{"model slug"}
    I -- claude-sdk --> J["claude-sonnet-4-6\ndirect Anthropic SDK"]
    I -- other slugs --> K["existing LLMGateway\ngemini, groq, cerebras, etc"]

    D & G & H --> J
    E & F --> L["claude-haiku-4-5-20251001\ndirect Anthropic SDK"]
```

---

## 8. Voice + Concierge Shared Session

```mermaid
flowchart TD
    subgraph Client
        CHAT["ConciergeRail\nsource=concierge"]
        VOICE["VoiceRail\nsource=voice"]
    end

    subgraph Session["shared session_id UUID"]
        T1["turn 1 user via concierge\nAnalyze my AI exposure"]
        T2["turn 2 assistant\nYour top AI holding is..."]
        T3["turn 3 user via voice\nWhat about HDFC Bank?"]
        T4["turn 4 assistant\nHDFC is 8% of portfolio"]
        T5["turn 5 user via concierge\nRebalance suggestion?"]
        T6["turn 6 assistant\nReduce AI by 2L"]
        T1 --> T2 --> T3 --> T4 --> T5 --> T6
    end

    CHAT -- source=concierge --> Routes["concierge_routes.py"]
    VOICE -- source=voice --> Routes

    Routes --> SVC["concierge_service.py"]
    SVC -- load_history all sources --> DB[("concierge_turns")]
    DB -- full mixed context --> SVC
    SVC -- append_turn with source tag --> DB
```

---

## 9. Database Schema

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string role
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        varchar title
        timestamptz created_at
        timestamptz updated_at
    }

    CHAT_TURNS {
        uuid id PK
        uuid session_id FK
        varchar role
        text content
        varchar model
        int tokens_in
        int tokens_out
        int elapsed_ms
        varchar source
        timestamptz created_at
    }

    USERS ||--o{ CHAT_SESSIONS : owns
    CHAT_SESSIONS ||--o{ CHAT_TURNS : contains
```

> `role` values: `user` or `assistant` — `source` values: `concierge` or `voice`
> `USERS` lives in Wagner SQLite; the FK is a logical reference only (no DB-level FK constraint across services).

---

## 10. API Wire Format

```mermaid
flowchart TD
    REQ["POST /api/v1/concierge\nAuthorization: Bearer JWT\nmessages: ConciergeMessage list\nmodel: ModelSlug\nsession_id: string or null\nsource: concierge or voice"]

    REQ --> F1["SSE frame 1 — session bootstrap\nsession_id: uuid string\ndelta: empty string"]
    F1 --> FN["SSE frames 2 to N — token deltas\ndelta: partial token string"]
    FN --> FFINAL["SSE final frame — metadata\nelapsed_ms, tokens_in, tokens_out\nmodel: string, provider: string"]
    FFINAL --> DONE["SSE sentinel\ndata: DONE"]

    FN --> ERR["SSE error frame on any failure\nerror: message string\ncode: error code string"]
```

---

## 11. Error Handling

```mermaid
flowchart TD
    START(["request enters concierge_routes"]) --> JWT{"JWT valid?"}

    JWT -- invalid or expired --> J401["HTTP 401\nfrontend redirects to login"]
    JWT -- valid --> MEM{"session DB lookup"}

    MEM -- not found or wrong owner --> M404["HTTP 404 or 403\nfrontend shows error turn"]
    MEM -- DB error --> M500["HTTP 500\nfrontend shows error turn"]
    MEM -- ok --> ANT{"Anthropic API call"}

    ANT -- AuthenticationError --> AE["SSE error frame\ncode: auth_error"]
    ANT -- RateLimitError --> RL["SSE error frame\ncode: rate_limit"]
    ANT -- overloaded 529 --> OL["SSE error frame\ncode: overloaded"]
    ANT -- APIConnectionError --> CN["SSE error frame\ncode: connection_error"]
    ANT -- stream ok --> PERSIST{"DB persist turns"}

    PERSIST -- write fails --> PF["log error silently\nstream already delivered to client"]
    PERSIST -- ok --> DONE["yield final meta frame\nyield data: DONE"]

    ABORT(["client AbortController.abort"]) --> CA["AbortError caught in hook\npatchTurn loading=false\nno error shown to user"]
```

---

## 12. Session State Machine

```mermaid
stateDiagram-v2
    [*] --> New : first POST without session_id
    New --> Active : INSERT concierge_sessions succeeds

    Active --> Streaming : Anthropic stream opens
    Streaming --> Active : stream closes and turns persisted

    Active --> Active : new turn arrives with same session_id
    Active --> Idle : no turns for 30 minutes
    Idle --> Active : new turn arrives with session_id
    Idle --> Expired : no turns for 7 days

    Expired --> [*] : row kept but history stops loading

    Active --> Abandoned : user calls clear on frontend
    Abandoned --> New : user sends next message
```

---

## 13. Implementation Order

```mermaid
flowchart TD
    S1["Step 1\nAlembic migration\nconcierge_sessions + concierge_turns tables"] --> S2
    S2["Step 2\nconcierge_memory_models.py\nConciergeSession + ConciergeTurn ORM"] --> S3
    S3["Step 3\nconcierge_memory_service.py\nget_or_create_session, load_history, append_turn"] --> S4
    S4["Step 4\nconcierge_schemas.py\nadd session_id, source, ConciergeStreamMeta"] --> S5
    S5["Step 5\nconcierge_service.py\nswap to Anthropic SDK + wire memory + caching"] --> S6
    S6["Step 6\nconcierge_routes.py\ninject AsyncSession + thread session_id"] --> S7
    S7["Step 7\nconfig.py\nANTHROPIC_API_KEY + model env vars"] --> S8
    S8["Step 8\nuseConciergeStream.ts\nsession_id ref + remove client history window"] --> S9
    S9["Step 9\nconcierge.types.ts\nsessionId + source fields"] --> S10
    S10["Step 10\nUpdate docs\narchitecture.md + concierge-plan.md"]

    style S1 fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff
    style S2 fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff
    style S3 fill:#1e1b4b,stroke:#6366f1,color:#e0e7ff
    style S4 fill:#0f172a,stroke:#334155,color:#e2e8f0
    style S5 fill:#0f172a,stroke:#334155,color:#e2e8f0
    style S6 fill:#0f172a,stroke:#334155,color:#e2e8f0
    style S7 fill:#0f172a,stroke:#334155,color:#e2e8f0
    style S8 fill:#064e3b,stroke:#10b981,color:#d1fae5
    style S9 fill:#064e3b,stroke:#10b981,color:#d1fae5
    style S10 fill:#064e3b,stroke:#10b981,color:#d1fae5
```

> Legend: **purple** = new DB + backend files, **dark** = modified backend, **green** = frontend + docs
