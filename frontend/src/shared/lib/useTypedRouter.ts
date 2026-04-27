import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { docIdParamsSchema, nodeIdParamsSchema } from '@/shared/lib/routeRecord'

/**
 * OOP router composable.
 * Wraps vue-router so consumers use typed class methods instead of raw refs.
 */
export class TypedRouter {
  private _router
  private _route

  constructor() {
    this._router = useRouter()
    this._route = useRoute()
  }

  get route() {
    return this._route
  }

  get router() {
    return this._router
  }

  /** Typed params for /graph/:docId and /path/:docId */
  get docParams() {
    return computed(() => {
      const result = docIdParamsSchema.safeParse(this._route.params)
      return result.success ? result.data : null
    })
  }

  /** Typed params for /quiz/:nodeId */
  get nodeParams() {
    return computed(() => {
      const result = nodeIdParamsSchema.safeParse(this._route.params)
      return result.success ? result.data : null
    })
  }

  toLibrary() {
    return this._router.push('/library')
  }

  toGraph(docId: number) {
    return this._router.push(`/graph/${docId}`)
  }

  toQuiz(nodeId: number) {
    return this._router.push(`/quiz/${nodeId}`)
  }

  toPath(docId: number) {
    return this._router.push(`/path/${docId}`)
  }

  toUpload() {
    return this._router.push('/upload')
  }

  toAchievements() {
    return this._router.push('/achievements')
  }
}

/** Factory composable returning an OOP TypedRouter instance */
export function useTypedRouter() {
  return new TypedRouter()
}
