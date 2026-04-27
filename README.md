# Feature Slice Architecture — Visual Learner

## Overview

This project uses **Feature Slice Architecture (FSA)** for the frontend and
**OOP / hexagonal layering** for the backend.

## Frontend layers

| Layer | Path | Responsibility |
|-------|------|---------------|
| `app` | `src/app` | Bootstrap, providers, router |
| `pages` | `src/pages` | Route-level composition of features |
| `features` | `src/features` | Self-contained features (UI + logic + API) |
| `widgets` | `src/widgets` | Complex shared components |
| `entities` | `src/entities` | Data models + lightweight stores |
| `shared` | `src/shared` | UI kit, utils, composables, design tokens |

## Backend layers

| Layer | Path | Responsibility |
|-------|------|---------------|
| `application` | `app/application.py` | Wire routes + middleware |
| `routers` | `app/routers` | HTTP handlers |
| `controllers` | `app/controllers` | Orchestration |
| `services` | `app/services` | Business logic (OOP, DI) |
| `repositories` | `app/repositories` | SQLAlchemy CRUD |
| `entities` | `app/entities` | Pydantic models |
| `dto` | `app/dto` | Request/response schemas |

## Quick links

- [Frontend layers](frontend/src/README.md)
- [Backend layers](backend/app/README.md)
