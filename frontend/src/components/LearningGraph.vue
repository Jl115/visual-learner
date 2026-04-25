<script setup lang="ts">
import { onMounted } from 'vue'
import { DataSet, Network } from 'vis-network'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const container = $ref<HTMLDivElement | null>(null)

onMounted(() => {
  if (!container || !store.graphData) return
  const nodes = new DataSet(store.graphData.nodes)
  const edges = new DataSet(store.graphData.edges)
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
  const network = new Network(container, { nodes, edges }, options)
  network.on('click', (params) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0]
      store.setActiveNode(nodeId)
    }
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
