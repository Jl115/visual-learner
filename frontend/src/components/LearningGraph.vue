<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { DataSet } from 'vis-data/peer/esm/vis-data.js'
import { Network, type DataInterfaceNodes, type DataInterfaceEdges } from 'vis-network'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const container = ref<HTMLDivElement | null>(null)

let networkInstance: Network | null = null

/** Staggered node entrance animation */
function animateNodesEntrance(
  ds: DataInterfaceNodes,
  ids: string[],
  opts: { staggerMs?: number; targetSizeField?: string } = {},
) {
  const { staggerMs = 80, targetSizeField = 'targetSize' } = opts
  const all = (ds as any).get(ids) as any[]
  const animated = all.map((n: any) => ({
    ...n,
    size: 1,
    opacity: 0,
    color: typeof n.color === 'string'
      ? n.color
      : { background: '#fff', border: '#fff', highlight: '#fff', opacity: 0 },
  }))
  ;(ds as any).update(animated)

  for (let i = 0; i < all.length; i++) {
    const n = all[i]
    const delay = i * staggerMs
    setTimeout(() => {
      const targetSize = (n as any)[targetSizeField] ?? 22
      const restoreColor = typeof n.originalColor === 'string'
        ? n.originalColor
        : { ...n.originalColor, opacity: 1 }
      ;(ds as any).update({
        id: n.id,
        size: targetSize,
        opacity: 1,
        color: restoreColor,
      })
    }, delay)
  }
}

onMounted(() => {
  if (!container.value || !store.graphData) return

  const rawNodes = store.graphData.nodes ?? []
  const rawEdges = store.graphData.edges ?? []
  const nodeIds: string[] = rawNodes.map((n: any) => n.id)

  const nodes = new DataSet(
    rawNodes.map((n: any) => ({
      ...n,
      targetSize: n.size ?? 22,
      originalColor: n.color ?? '#a5d8ff',
      color: { background: '#fff', border: '#fff', highlight: '#fff', opacity: 0 },
      size: 1,
      opacity: 0,
    })),
  ) as unknown as DataInterfaceNodes

  const edges = new DataSet(rawEdges) as unknown as DataInterfaceEdges

  const options = {
    nodes: {
      shape: 'dot',
      size: 22,
      font: { size: 14, face: 'Public Sans', color: '#1e1e1e' },
      borderWidth: 2,
      shadow: { enabled: true, color: 'rgba(0,0,0,0.08)', size: 12, x: 0, y: 4 },
    },
    edges: { width: 2, color: { color: '#e5e7eb', highlight: '#818cf8', hover: '#818cf8' } },
    physics: {
      forceAtlas2Based: { gravitationalConstant: -60, springLength: 120, springConstant: 0.08 },
      maxVelocity: 50,
      solver: 'forceAtlas2Based',
      timestep: 0.35,
      stabilization: { enabled: true, iterations: 800 },
    },
    interaction: { hover: true, tooltipDelay: 120, zoomView: true },
  }

  networkInstance = new Network(container.value, { nodes, edges }, options)

  networkInstance.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      store.setActiveNode(nodeId)
    }
  })

  networkInstance.once('stabilizationIterationsDone', () => {
    setTimeout(() => animateNodesEntrance(nodes, nodeIds, { staggerMs: 80 }), 50)
  })
})
</script>

<template>
  <div class="graph-wrapper">
    <div ref="container" class="graph-canvas"></div>
    <div class="graph-controls">
      <button class="ctrl-btn" @click="store.resetZoom">🔍 Reset</button>
      <button class="ctrl-btn" @click="store.togglePhysics">🌊 {{ store.physicsEnabled ? 'Freeze' : 'Unfreeze' }}</button>
    </div>
  </div>
</template>

<style scoped>
.graph-wrapper { flex: 1; position: relative; }
.graph-canvas { width: 100%; height: 100%; }
.graph-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  display: flex;
  gap: 8px;
}
.ctrl-btn {
  padding: 8px 14px;
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.92);
  border: 1px solid var(--color-border);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  cursor: pointer;
  transition: background 0.15s ease;
}
.ctrl-btn:hover { background: #fff; }
</style>
