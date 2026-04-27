# features layer

Independent, self-contained features with full UI + logic + API.

## Rules

- **No cross-feature imports.** `features/foo` must **NOT** import from `features/bar`.
- **Shared assets go to `shared/`**. If two features need the same component, promote it to `@/widgets` or `@/shared/ui`.
- **A feature slice** follows this internal structure:
  ```
  features/myFeature/
    ├── api/         — functions that call the backend
    ├── model/       — Pinia stores, business logic, types
    ├── ui/          — Vue components scoped to this feature
    └── index.ts     — public API barrel (only these exports are "allowed" to be imported)
  ```
- **Only `index.ts` is the public surface.** Other layers import a feature via `import { ... } from '@/features/myFeature'`.

## Current features

- `documentUpload` — Drag-and-drop PDF upload + status tracking
- `knowledgeGraph` — Force-directed graph canvas + controls
- `quizSession` — Interactive MCQ modal with scoring
- `documentLibrary` — Card grid of persisted documents
- `masteryProgress` — Streaks, badges, daily progress rings
- `achievements` — Gamification state / badges

## Import permissions

| May import from | Example |
|----------------|---------|
| `@/entities/*` | Data models, types |
| `@/shared/*`   | UI kit, utils, API helpers, composables |
| **NOT** `@/features/*` | No cross-talk between features |
