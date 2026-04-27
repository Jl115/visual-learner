# Services layer

Domain services: pure business logic, no HTTP and no SQLAlchemy session
management.

## Rules

- **All services are class-based** with constructor dependency injection.
- **No module-level mutable state** — constants (type aliases, transition tables)
  are OK; singleton instances are NOT.
- **Services MUST import `Container` from `app.container`** for manual wiring, or
  accept their dependencies in `__init__`.
- **Services must NOT import from `app.routers`**.

## Current services

| Service | Responsibilities |
|---------|-----------------|
| `OllamaClient` | async HTTP client for Ollama Cloud / local LLM |
| `NLPPipeline` | text tokenisation, keyword extraction |
| `GraphBuilder` | build node/edge tuples from document text |
| `GraphService` | orchestrate graph creation + persist via `NodeRepository` |
| `QuizEngine` | generate MCQs via `OllamaClient` |
| `state_machine` | document lifecycle transitions + `ProgressTracker` |
