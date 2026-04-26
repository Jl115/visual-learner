# Repositories layer

SQLAlchemy-based repositories implementing the generic CRUD interface defined
in `base_repository.py`.

## Rules

- **All repos extend `BaseRepository[Model, Domain]`**.
- **Constructor accepts `db: Session`** (injected by `Container`).
- **Repos must NOT import FastAPI, HTTP, or business services**.
- **Repos must NOT import from `app.routers` or `app.controllers`**.
