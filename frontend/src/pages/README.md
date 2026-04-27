# pages layer

Route-level composition of features.  Each page is a thin shell that
orchestrates multiple feature UIs into a full screen.

## Rules

- **A page is a pure composition layer** — it owns no state, no logic beyond layout.
- **Import features via their public barrel (`@/features/<name>`)**.
- **Import widgets for complex shared components** (`@/widgets/*`).
- **May import from any layer below** (`@/features`, `@/widgets`, `@/entities`, `@/shared`).

## Structure

```
pages/
  ├── HomePage.vue        — drag-drop upload + doc library preview
  ├── GraphPage.vue       — knowledge graph viewer + controls
  ├── QuizPage.vue        — quiz session + score panel
  └── index.ts            — barrel of all page components
```

## Lazy loading

Pages are lazy-loaded from `app/router.ts`:

```ts
const GraphPage = () => import('@/pages/GraphPage.vue')
```

This keeps the initial bundle small and only loads the code needed for the
active route.
