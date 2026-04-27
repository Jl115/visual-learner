<template>
  <div ref="networkRef" class="graph-canvas" />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import type { GraphNode, GraphEdge } from '@/features/knowledgeGraph/api/graph'
import { COLORS } from '@shared/lib/designTokens'

interface Props {
  nodes: GraphNode[]
  edges: GraphEdge[]
  physicsEnabled: boolean
}

const { nodes, edges, physicsEnabled } = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', nodeId: number | null): void
}>()

/* ── vis-network refs ─────────────────────────── */
const networkRef = ref<HTMLDivElement | null>(null)
let networkInstance: any = null
let nodesDataSet: any = null
let edgesDataSet: any = null

/* ── constants ───────────────────────────────── */
const DEFAULT_NODE_COLOR = COLORS.accentTeal
const EDGE_COLOR_BASE = '#555555'

const options = {
  nodes: {
    shape: 'dot',
    size: 16,
    font: {
      size: 14,
      color: COLORS.text,
      face: 'Inter, system-ui, sans-serif',
    },
    borderWidth: 2,
    borderWidthSelected: 4,
    shadow: {
      enabled: true,
      color: 'rgba(0,0,0,0.5)',
      size: 8,
      x: 2,
      y: 2,
    },
  },
  edges: {
    color: {
      color: EDGE_COLOR_BASE,
      highlight: COLORS.accentMint,
      hover: COLORS.accentMint,
    },
    smooth: {
      type: 'continuous',
      forceDirection: 'none',
    },
    arrows: {
      to: { enabled: true, scaleFactor: 0.6 },
    },
    shadow: {
      enabled: true,
      color: 'rgba(0,0,0,0.3)',
      size: 4,
      x: 1,
      y: 1,
    },
  },
  physics: {
    enabled: physicsEnabled,
    solver: 'forceAtlas2Based',
    forceAtlas2Based: {
      gravitationalConstant: -60,
      centralGravity: 0.01,
      springLength: 100,
      springConstant: 0.08,
      damping: 0.4,
      avoidOverlap: 0.5,
    },
    stabilization: {
      enabled: true,
      iterations: 1000,
      updateInterval: 50,
    },
    minVelocity: 0.75,
    timestep: 0.35,
    adaptiveTimestep: true,
  },
  interaction: {
    hover: true,
    tooltipDelay: 200,
    zoomView: true,
    dragView: true,
  },
}

/* ── helpers ──────────────────────────────────── */
function normalizeNodeColor(color?: string): string {
  if (!color) return DEFAULT_NODE_COLOR
  return color
}

function initNetwork() {
  if (!networkRef.value) return

  // Dynamic import avoids SSR / build issues
  import('vis-network').then(({ Network, DataSet }) => {
    nodesDataSet = new DataSet(
      nodes.map((n) => ({
        ...n,
        color: normalizeNodeColor(n.color),
        value: n.value ?? 5 + Math.random() * 10,
      }))
    )

    edgesDataSet = new DataSet(
      edges.map((e) => ({
        ...e,
        color: e.color || EDGE_COLOR_BASE,
      }))
    )

    networkInstance = new Network(
      networkRef.value!,
      { nodes: nodesDataSet, edges: edgesDataSet },
      options
    )

    // Click handler → emits selected node id
    networkInstance.on('selectNode', (params: any) => {
      if (params.nodes && params.nodes.length > 0) {
        emit('select', params.nodes[0] as number)
      }
    })

    networkInstance.on('deselectNode', () => {
      emit('select', null)
    })
  })
}

function updateData() {
  if (!nodesDataSet || !edgesDataSet) return
  nodesDataSet.clear()
  edgesDataSet.clear()
  nodesDataSet.add(
    nodes.map((n) => ({
      ...n,
      color: normalizeNodeColor(n.color),
      value: n.value ?? 5 + Math.random() * 10,
    }))
  )
  edgesDataSet.add(
    edges.map((e) => ({
      ...e,
      color: e.color || EDGE_COLOR_BASE,
    }))
  )
}

function updatePhysics() {
  if (!networkInstance) return
  networkInstance.setOptions({ physics: { enabled: physicsEnabled } })
}

/* ── expose imperative controls to parent ─────── */
defineExpose({
  resetZoom() {
    if (!networkInstance) return
    networkInstance.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } })
  },
  freezePhysics() {
    if (!networkInstance) return
    networkInstance.setOptions({ physics: { enabled: false } })
  },
  unfreezePhysics() {
    if (!networkInstance) return
    networkInstance.setOptions({ physics: { enabled: true } })
  },
  reLayout() {
    if (!networkInstance) return
    // Fade-out → stabilize → fade-in for smooth feel
    networkInstance.setOptions({
      physics: { enabled: true },
    })
    networkInstance.stabilize()
    networkInstance.fit({ animation: { duration: 2000, easingFunction: 'easeInOutQuad' } })
  },
})

/* ── lifecycle ────────────────────────────────── */
onMounted(() => {
  nextTick(initNetwork)
})

onBeforeUnmount(() => {
  if (networkInstance) {
    networkInstance.destroy()
    networkInstance = null
  }
})

/* ── watchers ─────────────────────────────────── */
watch(() => nodes, updateData, { deep: true })
watch(() => edges, updateData, { deep: true })
watch(() => physicsEnabled, updatePhysics)
</script>

<style scoped>
.graph-canvas {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background-color: var(--bg-color, #0f1116);
  border-radius: 0.5rem;
  overflow: hidden;
}
</style>
