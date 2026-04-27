# shared layer

Low-level, pure, reusable code with **zero** business knowledge.

## Rules

- **No imports from any other layer** (`@/features`, `@/entities`, `@/pages`, `@/widgets`, `@/app`).
- **Only `@/shared` imports from `@/shared`**.
- **Everything here is framework-agnostic** (or as close as possible).

## Sub-layers

| Folder | Purpose |
|--------|---------|
| `ui/`      | Vue components — the design-system primitives (BaseButton, ThemeProvider, DocumentStatus badge) |
| `lib/`     | TypeScript utilities, composables, router helpers, store factories, design tokens |
| `config/`  | Build-time constants, feature flags, environment helpers |
| `api/`     | Low-level HTTP client, interceptors, request/response transformers |

## `shared/ui/` vs `widgets/`

| | `shared/ui/` | `widgets/` |
|---|--------------|------------|
| Scope | **Any** project | **This** project only |
| Business logic | None | May contain mild domain-specific presentation |
| Examples | BaseButton, ThemeProvider | GraphCanvas, DocumentCard |

## Design Tokens

CSS custom properties + the `designTokens.ts` module provide a single source
of truth for colours, spacing, and fonts.
