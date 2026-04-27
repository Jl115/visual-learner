# Dependency injection (internal)

Production implementations of the `Container` and dependency providers.

- `app/di/container.py` — `Container` class (lazy init, no module-level state)
- `app/dependencies.py` — FastAPI `Depends()` factories for each service/repo

External code should import from the stable public facade:

```python
from app.container import Container, get_container
```

This decouples consumers from the internal `app.di` package layout.
