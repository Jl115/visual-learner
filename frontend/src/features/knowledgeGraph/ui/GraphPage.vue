<template>
  <div class="graph-page flex h-screen w-full flex-col">
    <!-- Header -->
    <header class="flex items-center justify-between px-6 py-4">
      <h1 class="text-xl font-semibold text-text-primary">
        Knowledge Graph
      </h1>
      <DocumentStatus v-if="docId" :docId="docId" />
    </header>

    <!-- Controls toolbar -->
    <div class="px-6 pb-3">
      <GraphControls
        :physics-enabled="graphStore.isPhysicsOn"
        :node-count="graphStore.nodeCount"
        :edge-count="graphStore.edgeCount"
        @reset-zoom="handleResetZoom"
        @toggle-physics="handleTogglePhysics"
        @re-layout="handleRelayout"
      />
    </div>

    <!-- Canvas -->
    <main class="flex-1 px-6 pb-6">
      <GraphCanvas
        ref="canvasRef"
        :nodes="graphStore.nodes"
        :edges="graphStore.edges"
        :physics-enabled="graphStore.isPhysicsOn"
        @select="handleNodeSelect"
      />
    </main>

    <!-- Node detail panel (placeholder for future phases) -->
    <aside
      v-if="graphStore.activeNodeId"
      class="absolute bottom-6 right-6 w-80 rounded-xl border border-border bg-surface p-4 shadow-lg"
    >
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-text-primary">Node selected</h3>
        <button class="text-text-muted hover:text-text-primary" @click="graphStore.setActiveNode(null)">
          ✕
        </button>
      </div>
      <p class="mt-2 text-xs text-text-muted">
        ID: {{ graphStore.activeNodeId }}
      </p>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useGraphStore } from '@/features/knowledgeGraph/model/store'
import { fetchGraph } from '@/features/knowledgeGraph/api/graph'
import GraphCanvas from '@/widgets/GraphCanvas.vue'
import GraphControls from '@/widgets/GraphControls.vue'
import DocumentStatus from '@/shared/ui/DocumentStatus.vue'

/* ── state ────────────────────────────────────── */
const route = useRoute()
const graphStore = useGraphStore()
const canvasRef = ref<InstanceType<typeof GraphCanvas> | null>(null)

const docId = ref<number | null>(null)

/* ── load graph data ──────────────────────────── */
async function loadGraph(id: number) {
  graphStore.setLoading(true)
  graphStore.setError(null)
  try {
    const payload = await fetchGraph(id)
    graphStore.setGraph(payload)
    docId.value = id
  } catch (err: any) {
    graphStore.setError(err?.message ?? 'Failed to load graph')
    // Fallback: demo data for local dev without backend
    graphStore.setGraph({
      document_id: id,
      nodes: [
        { id: 1, label: 'Theme A', color: '#4ECDC4', value: 12 },
        { id: 2, label: 'Theme B', color: '#FF6B6B', value: 8 },
        { id: 3, label: 'Theme C', color: '#FFE66D', value: 10 },
        { id: 4, label: 'Theme D', color: '#95E1D3', value: 6 },
      ],
      edges: [
        { id: 1, from: 1, to: 2, color: '#4ECDC4' },
        { id: 2, from: 2, to: 3, color: '#FF6B6B' },
        { id: 3, from: 3, to: 4, color: '#FFE66D' },
        { id: 4, from: 1, to: 4, color: '#4ECDC4' },
      ],
      node_count: 4,
      edge_count: 4,
    })
  } finally {
    graphStore.setLoading(false)
  }
}

/* ── event handlers ───────────────────────────── */
function handleNodeSelect(nodeId: number | null) {
  graphStore.setActiveNode(nodeId)
}

function handleResetZoom() {
  canvasRef.value?.resetZoom()
}

function handleTogglePhysics() {
  graphStore.togglePhysics()
  if (graphStore.isPhysicsOn) {
    canvasRef.value?.unfreezePhysics()
  } else {
    canvasRef.value?.freezePhysics()
  }
}

function handleRelayout() {
  canvasRef.value?.reLayout()
}

/* ── lifecycle ────────────────────────────────── */
onMounted(() => {
  const idParam = route.query.docId || route.params.docId
  const id = typeof idParam === 'string' ? parseInt(idParam, 10) : 1
  loadGraph(id)
})

watch(() => route.params.docId, (newVal) => {
  if (newVal) {
    const id = typeof newVal === 'string' ? parseInt(newVal, 10) : 1
    loadGraph(id)
  }
})
</script>

<style scoped>
.graph-page {
  background-color: #0f1116;
}
</style>
