<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { DataSet, Network } from 'vis-network'
import { useAppStore } from '../stores/app'
import { api } from '../services/api'

const store = useAppStore()
const container = $ref<HTMLDivElement | null>(null)
let network: Network | null = null

onMounted(() => {
  renderGraph()
})

function renderGraph() {
  if (!container || !store.graphData) return
  const nodes = new DataSet(store.graphData.nodes || [])
  const edges = new DataSet(store.graphData.edges || [])
  const options = {
    nodes: {
      shape: 'dot',
      font: { size: 14, face: 'Public Sans', color: '#1e1e1e' },
      borderWidth: 2,
      shadow: { enabled: true, color: 'rgba(0,0,0,0.08)', size: 12, x: 0, y: 4 },
    },
    edges: {
      width: 2,
      color: { color: '#e5e7eb', highlight: '#818cf8', hover: '#818cf8' },
      smooth: { type: 'continuous' },
    },
    physics: {
      forceAtlas2Based: { gravitationalConstant: -60, springLength: 120, springConstant: 0.08 },
      maxVelocity: 50,
      solver: 'forceAtlas2Based',
      timestep: 0.35,
      stabilization: { enabled: true, iterations: 800 },
    },
    interaction: { hover: true, tooltipDelay: 120, zoomView: true },
  }
  network = new Network(container, { nodes, edges }, options)
  network.on('click', async (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      const node = nodes.get(nodeId) as any
      store.setActiveNode(nodeId)
      store.nodeTitle = node.label || ''
      store.nodeSummary = node.title || ''
      // Fetch quizzes for this node
      try {
        const { data } = await api.get(`/quiz/${store.documentId}`, { params: { node_id: nodeId } })
        store.nodeQuizzes = data
      } catch {}
    }
  })
}

function resetZoom() { network?.fit({ animation: { duration: 400 } }) }
function togglePhysics() {
  store.physicsEnabled = !store.physicsEnabled
  network?.setOptions({ physics: { enabled: store.physicsEnabled } })
}
</script>

<template>
  <div class="graph-wrapper">
    <div ref="container" class="graph-canvas"></div>
    <div class="graph-controls">
      <button class="ctrl-btn" @click="resetZoom">🔍 Reset</button>
      <button class="ctrl-btn" @click="togglePhysics">🌊 {{ store.physicsEnabled ? 'Freeze' : 'Unfreeze' }}</button>
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
