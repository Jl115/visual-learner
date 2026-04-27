# widgets layer

Complex shared components that are too heavyweight or domain-specific for
`@/shared/ui` but used by **multiple** features.

## Rules

- **A widget may import from `@/features/*` but ONLY from `ui/` exports** (presentation, no store/model).
- **May import from `@/entities` and `@/shared`**.
- **Must NOT import from `@/pages` or `@/app`**.

## When to promote a component → widget

1. It is used by **two or more features**.
2. It contains **no feature-specific business logic** (state, stores).
3. It is **too complex** for a simple primitive in `@/shared/ui`.

## Current widgets

| Widget | Used by | Notes |
|--------|---------|-------|
| *(none yet — scaffolded in advance)* | — | Add when GraphCanvas or DocumentCard is reused across features |

## Structure

```
widgets/
  ├── GraphCanvas.vue   — vis-network wrapper with dark theme + pastel palette
  ├── DocumentCard.vue  — card component shared between Library + Mastery views
  └── index.ts          — barrel
```
