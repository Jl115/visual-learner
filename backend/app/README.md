# Backend architecture

Python FastAPI backend organised by **layers**, not by function.

```
app/
├── main.py              — app factory (create_app)
├── application.py       — route registry + middleware wiring
├── container.py         — DI container re-export (thin facade)
├── config/              — Pydantic Settings, env vars, constants
├── common/              — pure utilities, exceptions, type aliases
├── middleware/          — FastAPI middleware (errors, CORS, auth)
├── routers/             — FastAPI route modules (thin controllers)
├── controllers/         — HTTP-agnostic orchestration logic
├── services/            — Domain services (OOP, __init__ DI only)
├── repositories/        — SQLAlchemy repository classes (OOP)
├── entities/            — Pydantic domain models
├── dto/                 — Request/response schemas (Pydantic)
├── database/            — SQLAlchemy models, connection, migrations
└── di/                  — DI container internals
```

## Layer rules

| Layer | May import from | Must NOT import from |
|-------|----------------|----------------------|
| **common** | stdlib, third-party | *nothing else* |
| **config** | stdlib, third-party | domain (entities, services) |
| **database** | stdlib, third-party, config | routers, services |
| **entities** | stdlib, third-party, common, config | routers, services, repositories |
| **dto** | entities, common | services, repositories |
| **repositories** | entities, database, common | routers, controllers, services |
| **services** | repositories, entities, common, config | routers, controllers |
| **controllers** | services, entities, dto, common | routers |
| **routers** | controllers, services, dto, entities | *nothing else* |
| **application** | routers, middleware, container | *nothing else* (pure wiring) |
| **container** | repositories, services, config, database | routers, application |

## DI container

`Container` lives in `app.di.container`.  It lazily-initialises every dependency
and accepts a `Session` via `bind_session(db)` for request-scoped repositories.

Import from the stable public facade:

```python
from app.container import Container, get_container
```

## OOP mandate

- All services MUST be class-based with `__init__` DI.
- Repositories MUST be class-based and accept `db: Session`.
- No module-level mutable state in `services/` or `repositories/`.
