<<template>
  <div class="graph-page flex h-screen w-full flex-col">
    <!-- Header -->
    <header class="flex items-center justify-between px-6 py-4">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-semibold text-text-primary">
          Knowledge Graph
        </h1>
        <!-- Mastery progress badge -->
        <span
          v-if="masteryStore.stats"
          class="text-sm font-medium text-white px-3 py-1 rounded-full bg-slate-700/60"
        >
          {{ masteryStore.learnedCount }}/{{ masteryStore.stats.total_nodes }} mastered ({{ masteryStore.masteryPercent }}%)
        </span>
      </div>
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

    <!-- Main layout: Canvas + Mastery Side Panel -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Canvas -->
      <main class="flex-1 px-6 pb-6">
        <GraphCanvas
          ref="canvasRef"
          :nodes="displayNodes"
          :edges="displayEdges"
          :physics-enabled="graphStore.isPhysicsOn"
          @select="handleNodeSelect"
        />
      </main>

      <!-- Mastery Side Panel -->
      <aside
        v-if="masteryStore.activeState"
        class="w-80 shrink-0 border-l border-border bg-surface p-4 text-white"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-text-primary">Node Details</h3>
          <button
            class="text-text-muted hover:text-text-primary text-xs px-2 py-1 rounded hover:bg-surface-hover"
            @click="masteryStore.selectNode(null)"
          >
            ✕ Close
          </button>
        </div>

        <!-- Node info -->
        <div class="mb-4 rounded-lg bg-surface p-3 border border-border">
          <div class="text-xs text-text-muted uppercase tracking-wider mb-1">Label</div>
          <div class="text-sm font-medium text-white">{{ masteryStore.activeState.label }}</div>
        </div>

        <!-- State display -->
        <div class="mb-4 rounded-lg p-3 border"
          :style="{ backgroundColor: stateBgColor, borderColor: stateBorderColor }"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase tracking-wider">Mastery State</span>
            <span
              class="px-2 py-0.5 rounded-full text-xs font-semibold"
              :style="{ backgroundColor: masteryStore.activeState.color, color: '#1a1c23' }"
            >
              {{ stateLabel }}
            </span>
          </div>
          <div class="text-xs text-text-muted">
            Review count: <span class="font-mono">{{ masteryStore.activeState.review_count }}</span>
          </div>
          <div v-if="masteryStore.activeState.last_reviewed" class="text-xs text-text-muted mt-1">
            Last reviewed: <span class="font-mono">{{ formatDate(masteryStore.activeState.last_reviewed) }}</span>
          </div>
        </div>

        <!-- Countdown / review reminder -->
        <div v-if="masteryStore.activeState.state !== 'learned'" class="mb-4 rounded-lg bg-surface p-3 border border-border">
          <div class="text-xs text-text-muted mb-1">Next review</div>
          <div class="text-sm font-medium">{{ timeUntilReview }}</div>
        </div>

        <!-- State transition buttons -->
        <div class="flex flex-col gap-2">
          <button
            v-if="masteryStore.activeState.state !== 'learned'"
            class="rounded-lg px-3 py-2 text-sm font-medium transition-colors"
            style="background-color: #9CAF88; color: #1a1c23;"
            @click="handleSetState('learned')"
          >
            ✅ Mark as Learned
          </button>
          <button
            v-if="masteryStore.activeState.state !== 'reviewing'"
            class="rounded-lg bg-surface px-3 py-2 text-sm font-medium transition-colors hover:bg-surface-hover border border-border"
            @click="handleSetState('reviewing')"
          >
            📖 Mark as Reviewing
          </button>
          <button
            v-if="masteryStore.activeState.state !== 'new'"
            class="rounded-lg bg-surface px-3 py-2 text-sm font-medium transition-colors hover:bg-surface-hover border border-border text-text-muted"
            @click="handleSetState('new')"
          >
            🔄 Reset to New
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useGraphStore } from '@/features/knowledgeGraph'
import { useMasteryStore } from '@/features/masteryProgress'
import { fetchGraph } from '@/features/knowledgeGraph/api/graph'
import GraphCanvas from '@/widgets/GraphCanvas.vue'
import GraphControls from '@/widgets/GraphControls.vue'
import DocumentStatus from '@/shared/ui/DocumentStatus.vue'

/* ── state ────────────────────────────────────── */
const route = useRoute()
const graphStore = useGraphStore()
const masteryStore = useMasteryStore()
const canvasRef = ref<InstanceType<typeof GraphCanvas> | null>(null)

const docId = ref<number | null>(null)

/* ── computed for display --> */
const displayNodes = computed(() => {
  if (masteryStore.nodes.length > 0) {
    return masteryStore.nodes.map(n => ({
      id: n.id,
      label: n.label,
      color: n.color,
      value: 10 + (n.review_count || 0) * 2,
    }))
  }
  return graphStore.nodes
})

const displayEdges = computed(() => {
  if (masteryStore.edges.length > 0) {
    return masteryStore.edges
  }
  return graphStore.edges
})

const stateLabel = computed(() => {
  const s = masteryStore.activeState?.state
  if (!s) return 'Unknown'
  return { new: 'New', reviewing: 'Reviewing', learned: 'Learned' }[s] || s
})

const stateBgColor = computed(() => {
  const s = masteryStore.activeState?.state
  if (s === 'new') return 'rgba(221,160,221,0.1)'
  if (s === 'reviewing') return 'rgba(255,218,185,0.1)'
  if (s === 'learned') return 'rgba(156,175,136,0.1)'
  return 'transparent'
})

const stateBorderColor = computed(() => {
  const s = masteryStore.activeState?.state
  if (s === 'new') return '#DDA0DD'
  if (s === 'reviewing') return '#FFDAB9'
  if (s === 'learned') return '#9CAF88'
  return 'var(--border)'
})

const timeUntilReview = computed(() => {
  const last = masteryStore.activeState?.last_reviewed
  if (!last) return 'Not yet reviewed'
  const days = Math.floor((Date.now() - new Date(last).getTime()) / (1000 * 60 * 60 * 24))
  if (days < 1) return 'Today'
  if (days === 1) return 'Yesterday'
  return `${days} days ago`
})

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

/* ── load graph data ──────────────────────────── */
async function loadGraph(id: number) {
  graphStore.setLoading(true)
  graphStore.setError(null)
  try {
    // Load both traditional graph + mastery-enriched graph
    const [payload, masteryPayload] = await Promise.all([
      fetchGraph(id),
      masteryStore.loadMasteryGraph(id),
    ])
    graphStore.setGraph(payload)
    docId.value = id
    masteryStore.loadStats(id)
  } catch (err: any) {
    // If mastery API fails, fall back to traditional graph
    graphStore.setError(err?.message ?? 'Failed to load graph')
    try {
      const payload = await fetchGraph(id)
      graphStore.setGraph(payload)
      docId.value = id
    } catch (e2) {
      // Demo fallback
      graphStore.setGraph({
        document_id: id,
        nodes: [
          { id: 1, label: 'Theme A', color: '#DDA0DD', value: 12 },
          { id: 2, label: 'Theme B', color: '#FFDAB9', value: 8 },
          { id: 3, label: 'Theme C', color: '#9CAF88', value: 10 },
          { id: 4, label: 'Theme D', color: '#DDA0DD', value: 6 },
        ],
        edges: [
          { id: 1, from: 1, to: 2, color: '#555555' },
          { id: 2, from: 2, to: 3, color: '#555555' },
          { id: 3, from: 3, to: 4, color: '#555555' },
          { id: 4, from: 1, to: 4, color: '#555555' },
        ],
        node_count: 4,
        edge_count: 4,
      })
    }
  } finally {
    graphStore.setLoading(false)
  }
}

/* ── event handlers ───────────────────────────── */
function handleNodeSelect(nodeId: number | null) {
  graphStore.setActiveNode(nodeId)
  masteryStore.selectNode(nodeId)
}

function handleSetState(newState: 'new' | 'reviewing' | 'learned') {
  if (masteryStore.activeState?.id) {
    masteryStore.setNodeState(masteryStore.activeState.id, newState)
  }
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
