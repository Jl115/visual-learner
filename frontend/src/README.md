# Frontend architecture

This is a Vue 3 + Vite + Electron frontend using **Feature Slice Architecture**.

## Layers

| Layer | Folder | Responsibility |
|-------|--------|---------------|
| `app` | `app/` | Entry point, providers, router, composition |
| `pages` | `pages/` | Route-level pages (lazy-loadable) |
| `features` | `features/` | Independent features with UI + logic + API |
| `widgets` | `widgets/` | Complex shared components |
| `entities` | `entities/` | Data models, TypeScript types, lightweight stores |
| `shared` | `shared/` | UI kit, utilities, composables, design tokens |

## Key layers

- **[app](app/README.md)** — Application shell
- **[features](features/README.md)** — Feature slices (6 feature areas)
- **[shared](shared/README.md)** — Reusable UI primitives and helpers

## Import rules

```
app     → pages, features, widgets, entities, shared
pages   → features, widgets, entities, shared
widgets → features/ui, entities, shared
features → entities, shared          (NOT other features!)
entities → shared
shared   → shared                    (No other layer!)
```

## Path aliases

Defined in `vite.config.ts` and `tsconfig.json`:

| Alias | Points to |
|-------|-----------|
| `@/` | `src/` |
| `@app/` | `src/app/` |
| `@pages/` | `src/pages/` |
| `@features/` | `src/features/` |
| `@widgets/` | `src/widgets/` |
| `@entities/` | `src/entities/` |
| `@shared/` | `src/shared/` |

## ESLint

The `.eslintrc.cjs` enforces layer import ordering via `import/order` and blocks
forbidden cross-layer imports via `@typescript-eslint/no-restricted-imports`.
