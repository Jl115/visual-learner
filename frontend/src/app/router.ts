import { createRouter, createWebHistory } from 'vue-router'
import GraphPage from '@features/knowledgeGraph/ui/GraphPage.vue'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/graph/:docId?',
      name: 'Graph',
      component: GraphPage,
      props: true,
    },
    {
      path: '/',
      redirect: '/graph',
    },
  ],
})

export default router
