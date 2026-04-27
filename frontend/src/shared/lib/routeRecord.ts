import { z } from 'zod'

export interface RouteMeta {
  /** Whether the route requires an active document */
  needsDocument?: boolean
  /** Whether the route requires an active node */
  needsNode?: boolean
  /** Human-readable label for nav */
  label?: string
  /** Icon name for nav */
  icon?: string
  [key: string]: unknown
  [key: number]: unknown
  [key: symbol]: unknown
}

export class RouteRecord {
  /** Route path */
  path: string
  /** Lazy component loader */
  component: () => Promise<typeof import('*.vue')>
  /** Route name */
  name?: string
  /** Typed meta fields */
  meta: RouteMeta
  /** Child route definitions */
  children?: RouteRecord[]

  constructor(options: {
    path: string
    component: () => Promise<typeof import('*.vue')>
    name?: string
    meta?: RouteMeta
    children?: RouteRecord[]
  }) {
    this.path = options.path
    this.component = options.component
    this.name = options.name
    this.meta = {
      needsDocument: false,
      needsNode: false,
      ...options.meta,
    }
    this.children = options.children
  }
}

// ── Zod schemas for route params ─────────────────
export const docIdParamsSchema = z.object({
  docId: z.coerce.number().int().positive(),
})

export const nodeIdParamsSchema = z.object({
  nodeId: z.coerce.number().int().positive(),
})

export type DocIdParams = z.infer<typeof docIdParamsSchema>
export type NodeIdParams = z.infer<typeof nodeIdParamsSchema>
