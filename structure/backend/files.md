# Backend Application Structure

> **Core principle**: 1 file = 1 responsibility. Async everywhere. The route layer is a thin shell over services; services are thin shells over repositories + clients.
> Soft caps: 200 lines per route module · 300 lines per service module. Beyond that, split.

---

## Layered architecture

```
┌─────────────────────────────────────────────────┐
│  HTTP boundary (FastAPI routes)                 │
│  Pydantic request/response models               │
│  Authentication, validation, error mapping      │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Service layer (business logic, async)          │
│  Cross-resource orchestration, transactions     │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│  Repository / data layer                        │
│  SQLAlchemy 2.0 async sessions                  │
│  Vector store, caches, file I/O                 │
└──────────────────────┬──────────────────────────┘
                       ▼
                ┌─────────────┐
                │  Postgres   │
                │  Redis      │
                │  Disk / S3  │
                └─────────────┘
```

**Rule**: routes don't import from `models/` directly. Services do. Repositories don't import from `routes/`. Reverse imports are linter errors.

---

## Directory layout

```
backend/
├── app/
│   ├── main.py                       FastAPI app factory + lifespan
│   ├── core/
│   │   ├── config.py                 pydantic-settings — single Settings class
│   │   ├── database.py               async engine, session factory, get_db dep
│   │   ├── logging.py                setup_logging() + get_logger() facade
│   │   └── security.py               JWT + bcrypt helpers
│   ├── models/
│   │   ├── __init__.py               re-export all ORM classes
│   │   ├── user.py                   one ORM class per file
│   │   ├── holding.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── auth.py                   Pydantic v2 request/response models
│   │   ├── portfolio.py
│   │   └── ...
│   ├── routes/
│   │   ├── __init__.py               api_router aggregator
│   │   ├── health.py                 GET /health
│   │   ├── auth.py
│   │   ├── portfolio.py              endpoints + Pydantic models, no logic
│   │   └── ...
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── memory.py
│   │   ├── embedding.py
│   │   └── brokers/
│   │       ├── base.py               BrokerSource ABC + Holding model
│   │       ├── csv_sources.py        CSV-driven plugins
│   │       ├── angel_one.py          API-driven plugin
│   │       ├── aggregator.py         cross-source roll-up + treemap
│   │       └── registry.py           process-wide singleton dict
│   ├── repositories/
│   │   ├── user_repo.py              all DB queries for User
│   │   └── holding_repo.py
│   └── clients/
│       ├── kite_client.py            outbound HTTP / SDK wrappers
│       └── llm_client.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   └── broker_csvs/              sample CSV exports
│   ├── unit/                         no I/O, no network
│   ├── integration/                  TestClient + real DB session
│   └── test_brokers.py
├── scripts/
│   ├── dev_brokers.py                CLI for hand-testing portfolio API
│   └── ...
├── notebooks/
│   └── portfolio_dev.ipynb           dual-mode (in-process / live HTTP) playground
├── docs/
│   ├── BROKERS.md                    setup + endpoint reference per source
│   └── ...
├── data/                             generated artefacts (gitignored)
├── pdm.toml                          PDM config — uses uv backend
├── pyproject.toml                    deps + ruff + pytest config
└── pip.conf                          require-virtualenv
```

---

## Module responsibilities

### `core/`

Cross-cutting plumbing. Nothing here imports from `routes/`, `services/`, or `models/`.

| File | Owns |
|------|------|
| `config.py` | The single `Settings` class. Reads `.env` + env vars. Anything that's environment-specific lives here. |
| `database.py` | Async SQLAlchemy engine, `async_session` factory, the `get_db` dependency. |
| `logging.py` | `setup_logging()` (called once in lifespan) and `get_logger(name)`. Wraps `alphaforge-logger`. |
| `security.py` | JWT encode/decode, password hash/verify. No business logic. |

### `models/` (SQLAlchemy ORM)

One ORM class per file. Use `Mapped[...]` + `mapped_column(...)` (SQLAlchemy 2.0 style). Foreign keys live on the **child** side.

```python
# models/holding.py
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    quantity: Mapped[float]
    avg_price: Mapped[float]

    user: Mapped["User"] = relationship(back_populates="holdings")
```

### `schemas/` (Pydantic v2)

Wire shapes for the API boundary — separate from ORM models so DB changes don't break the API contract. Suffix request models with `Request`, response with `Response` or `DTO`.

```python
# schemas/portfolio.py
from pydantic import BaseModel, Field


class CreateHoldingRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float = Field(..., gt=0)
    avg_price: float = Field(..., gt=0)


class HoldingResponse(BaseModel):
    id: int
    symbol: str
    quantity: float
    avg_price: float
    last_price: float
    pnl: float
```

### `routes/`

One router per resource. Files mirror REST nouns (`portfolio.py`, `auth.py`, `dashboard.py`). Routers are mounted in `routes/__init__.py`:

```python
# routes/__init__.py
from fastapi import APIRouter

from app.routes.health import router as health_router
from app.routes.portfolio import router as portfolio_router
# ...

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
```

Inside a route module:

```python
# routes/portfolio.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.portfolio import CreateHoldingRequest, HoldingResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.post("/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(payload: CreateHoldingRequest, db: AsyncSession = Depends(get_db)):
    service = PortfolioService(db)
    try:
        holding = await service.create(payload)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    return holding
```

**Rules:**
- A route handler is ≤ 30 lines. Anything longer means the service is too thin.
- No `from app.models.* import *` at the top of a route. Routes operate on Pydantic schemas; the service deals with ORM objects.
- All paths kebab-case (`/portfolio/risk-meter`, not `/portfolio/risk_meter`).
- Query/path params snake_case (matches Python convention; FastAPI handles the JSON conversion automatically for response models).

### `services/`

Where the business logic lives. Each service is a class (so it can hold a session + dependencies cleanly) or, for stateless helpers, a module of free functions.

```python
# services/portfolio_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.holding_repo import HoldingRepository
from app.schemas.portfolio import CreateHoldingRequest


class PortfolioService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = HoldingRepository(db)

    async def create(self, payload: CreateHoldingRequest) -> Holding:
        if payload.quantity <= 0:
            raise ValueError("quantity must be positive")
        return await self._repo.create(**payload.model_dump())
```

**Plug-in pattern (brokers, providers):** when a category of source needs to be open-ended, define an ABC + a registry dict so adding a new source is one file.

```python
# services/brokers/base.py
class BrokerSource(ABC):
    slug: str
    label: str
    kind: SourceKind

    async def fetch(self) -> list[Holding]: ...
    def parse(self, stream: IO[bytes]) -> list[Holding]: ...
```

### `repositories/`

The only place SQLAlchemy queries live. One repo per aggregate root. Everything here is async.

```python
# repositories/holding_repo.py
class HoldingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, holding_id: int) -> Holding | None:
        return await self._db.get(Holding, holding_id)

    async def list_for_user(self, user_id: int) -> list[Holding]:
        result = await self._db.execute(
            select(Holding).where(Holding.user_id == user_id),
        )
        return list(result.scalars())
```

### `clients/`

Outbound HTTP / SDK wrappers. One file per upstream. Always async (`httpx.AsyncClient`). Encapsulate auth + retries here so services stay clean.

---

## Cross-cutting conventions

### Async

- Every route is `async def`.
- Every service method that touches I/O is `async def`.
- Synchronous helpers live in `app/utils/` (no `app/utils/__init__.py` reaches across layers).

### Imports

- Absolute only: `from app.core.config import settings`.
- Sort with ruff (stdlib → 3rd-party → app, blank lines between).
- `from __future__ import annotations` at the top of every module (lets you use `X | None` everywhere).

### Error mapping

Services raise plain Python exceptions (`ValueError`, `RuntimeError`, custom subclasses). Routes catch and translate to `HTTPException` — never the other way around. This keeps services framework-free and unit-testable.

### Logging

Always via `get_logger("module.name")`. Module names mirror the dotted path (`routes.portfolio`, `services.brokers.angel_one`). Never call `logging.getLogger()` directly; the wrapper centralises file rotation.

---

## Testing layout

```
tests/
├── conftest.py            # shared fixtures: db_session, client, mock_kite, …
├── fixtures/
│   └── broker_csvs/       # sample CSVs per source
├── unit/
│   ├── test_aggregator.py
│   └── test_csv_parsers.py
├── integration/
│   ├── test_portfolio_api.py
│   └── test_screener_api.py
└── test_brokers.py        # happens to span both — that's fine, organize by domain
```

- **Unit** = no DB, no network, no FastAPI app. Pure functions and class methods.
- **Integration** = real `TestClient(app)` + a transactional DB session that rolls back at end-of-test.
- One `Test<Subject>` class per logical grouping. Test method names: `test_<does_what>_<under_what_condition>`.

---

## Dependency injection

FastAPI's `Depends()` for request-scoped dependencies (DB session, current user). For service-level dependencies (broker registry, embedding client), use module-level singletons created in `main.py`'s lifespan.

```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    embed_svc = get_embedding_service()  # singleton
    yield
    await embed_svc.close()
```

---

## File-size discipline

| File type | Soft cap | Action when exceeded |
|-----------|----------|----------------------|
| Route module | 200 lines | Split by sub-resource (`portfolio_holdings.py`, `portfolio_sources.py`). |
| Service module | 300 lines | Extract a sub-service or move helpers to `utils/`. |
| Schema module | 200 lines | Group by sub-feature; one file per top-level resource is fine. |
| Test module | 400 lines | Split by `TestClass` — one feature per file. |
| ORM model | 100 lines | Push computed properties to a service. |

---

## Anti-patterns

- ❌ Importing ORM models inside route modules.
- ❌ `db.commit()` inside a route — wrap in a service that owns the transaction boundary.
- ❌ Synchronous `requests` calls — always `httpx.AsyncClient`.
- ❌ Catching bare `Exception` without re-raising or logging.
- ❌ Mutable module-level state outside `registry.py` and lifespan singletons.
- ❌ `print()` — always `get_logger(...).info(...)`.
- ❌ Hard-coded secrets/URLs — must come through `Settings`.
