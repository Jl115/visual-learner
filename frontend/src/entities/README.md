# entities layer

Data models, TypeScript interfaces, and lightweight stores that represent
domain concepts shared across the application.

## Rules

- **No business logic** — entities describe *what* data looks like, not *how* it behaves.
- **May import from `@/shared`** for utilities, types, and base classes.
- **Must NOT import from `@/features`, `@/widgets`, `@/pages`, or `@/app`**. If an entity needs to reference a feature concept, the dependency is inverted — the feature imports the entity.

## Responsibilities

| File / Folder | Purpose |
|---------------|---------|
| `document/`   | `Document` type, document status enum CRUD store |
| `node/`      | `KnowledgeNode` type, node store (read-only) |
| `quiz/`      | `Quiz`, `Question` types |
| `index.ts`   | Barrels re-exporting all entity types |

## Example

```ts
// entities/document/index.ts
export interface Document {
  id: number
  title: string
  status: DocumentStatus
  createdAt: Date
}

export { useDocumentStore } from './store'
```

External code imports entities as:

```ts
import type { Document, DocumentStatus } from '@/entities/document'
```
