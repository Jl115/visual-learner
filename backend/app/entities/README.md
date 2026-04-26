# Entities layer

Pydantic domain models representing the core data structures.

## Rules

- **Pydantic v2 models** — strict validation.
- **No dependencies on routers, services, or repositories**.
- **May import from `app.common` or `app.config`** for type aliases and enums.

## Current entities

| Model | Description |
|-------|-------------|
| `Document` | Uploaded file metadata + status |
| `Node` | Knowledge graph node (label, summary, position, theme) |
| `Edge` | Relationship between two nodes |
| `Quiz` / `Question` | MCQ with options and correct index |
