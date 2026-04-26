import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { useDocumentStore } from '@/entities/document'
import { RouteRecord } from '@/shared/lib/routeRecord'

/* ── Feature-owned route definitions (FSA) ─────────────────────────── */
const library = new RouteRecord({
  path: '/library',
  name: 'Library',
  component: () => import('@/features/documentLibrary/ui/LibraryPage.vue'),
  meta: { label: 'Library', icon: '📚' },
})

const graph = new RouteRecord({
  path: '/graph/:docId',
  name: 'Graph',
  component: () => import('@/features/knowledgeGraph/ui/GraphPage.vue'),
  meta: { needsDocument: true, label: 'Graph', icon: '🕸️' },
})

const quiz = new RouteRecord({
  path: '/quiz/:nodeId',
  name: 'Quiz',
  component: () => import('@/features/quizSession/ui/QuizPage.vue'),
  meta: { needsNode: true, label: 'Quiz', icon: '❓' },
})

const pathPage = new RouteRecord({
  path: '/path/:docId',
  name: 'Path',
  component: () => import('@/features/masteryProgress/ui/PathPage.vue'),
  meta: { needsDocument: true, label: 'Path', icon: '🛤️' },
})

const achievements = new RouteRecord({
  path: '/achievements',
  name: 'Achievements',
  component: () => import('@/features/achievements/ui/AchievementsPage.vue'),
  meta: { label: 'Achievements', icon: '🏆' },
})

const upload = new RouteRecord({
  path: '/upload',
  name: 'Upload',
  component: () => import('@/features/documentUpload/ui/UploadPage.vue'),
  meta: { label: 'Upload', icon: '⬆️' },
})

/** Exported for nav generation in Sidebar */
export const routeTable: RouteRecord[] = [library, graph, quiz, pathPage, achievements, upload]

/** Convert OOP RouteRecord → vue-router raw record */
function toRaw(record: RouteRecord): RouteRecordRaw {
  return {
    path: record.path,
    name: record.name,
    component: record.component,
    meta: record.meta,
    children: record.children?.map(toRaw),
  }
}

const routes: RouteRecordRaw[] = routeTable.map(toRaw)

/* ── Router instance ───────────────────────────────────────────────── */
const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    { path: '/', redirect: '/library' },
    ...routes,
    { path: '/:pathMatch(.*)*', redirect: '/library' },
  ],
})

/* ── NavigationGuard ─────────────────────────────────────────────────── */
router.beforeEach((to, _from, next) => {
  const docStore = useDocumentStore()

  // Redirect root '/' → /upload if no docs exist, otherwise /library (handled by static redirect above)
  if (to.path === '/library' && docStore.count === 0) {
    next('/upload')
    return
  }

  if (to.meta.needsDocument === true && docStore.count === 0) {
    next('/upload')
    return
  }

  next()
})

export default router

/** Factory for creating a fresh router instance (e.g. tests) */
export function createAppRouter() {
  return router
}
