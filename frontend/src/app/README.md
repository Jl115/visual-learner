# app layer

Application shell: entry points, providers, router layout.

## Rules

- **No business logic.**  Only wiring: mount the Vue app, init Pinia/Vue-Router, inject global providers.
- **Router lives here** (`router.ts`) — routes are lazy-loaded from `@/pages/*`.
- **Providers live here** (`providers/` — ThemeProvider, error boundaries, etc.).
- **May import from any layer** below it: `@/pages`, `@/features`, `@/widgets`, `@/entities`, `@/shared`.

## Files

| File | Purpose |
|------|---------|
| `main.ts` | Vue app bootstrap (createApp, use Pinia, use router, mount) |
| `App.vue` | Root layout shell: ThemeProvider → RouterView → global toasts/error boundary |
| `router.ts` | Vue Router setup; `component: () => import('@/pages/...')` for page-level code-splitting |
| `providers/` | Global providers that wrap the entire app |
