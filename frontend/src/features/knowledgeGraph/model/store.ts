import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { GraphNode, GraphEdge, GraphPayload } from '@/features/knowledgeGraph/api/graph'

export const useGraphStore = defineStore('graph', () => {
  // ── State ──────────────────────────────────────
  const nodes = ref<GraphNode[]>([])
  const edges = ref<GraphEdge[]>([])
  const documentId = ref<number | null>(null)
  const physicsEnabled = ref(true)
  const activeNodeId = ref<number | null>(null)
  const zoomScale = ref(1.0)
  const panOffset = ref({ x: 0, y: 0 })
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────
  const isPhysicsOn = computed(() => physicsEnabled.value)
  const hasActiveNode = computed(() => activeNodeId.value !== null)
  const zoomPercent = computed(() => Math.round(zoomScale.value * 100))
  const nodeCount = computed(() => nodes.value.length)
  const edgeCount = computed(() => edges.value.length)
  const graphData = computed(() => ({
    nodes: nodes.value,
    edges: edges.value,
  }))

  // ── Actions ─────────────────────────────────────
  const setGraph = (payload: GraphPayload) => {
    documentId.value = payload.document_id
    nodes.value = payload.nodes
    edges.value = payload.edges.map(e => ({ ...e, from: e.from ?? e.source ?? e.id }))
  }

  const clearGraph = () => {
    nodes.value = []
    edges.value = []
    documentId.value = null
    activeNodeId.value = null
  }

  const togglePhysics = () => {
    physicsEnabled.value = !physicsEnabled.value
  }

  const setPhysics = (v: boolean) => {
    physicsEnabled.value = v
  }

  const setActiveNode = (id: number | null) => {
    activeNodeId.value = id
  }

  const setZoom = (scale: number) => {
    zoomScale.value = scale
  }

  const zoomIn = (step = 0.1) => {
    zoomScale.value = Math.min(3.0, zoomScale.value + step)
  }

  const zoomOut = (step = 0.1) => {
    zoomScale.value = Math.max(0.2, zoomScale.value - step)
  }

  const resetZoom = () => {
    zoomScale.value = 1.0
    panOffset.value = { x: 0, y: 0 }
  }

  const setPan = (x: number, y: number) => {
    panOffset.value = { x, y }
  }

  const setLoading = (v: boolean) => {
    loading.value = v
  }

  const setError = (msg: string | null) => {
    error.value = msg
  }

  const reset = () => {
    nodes.value = []
    edges.value = []
    documentId.value = null
    physicsEnabled.value = true
    activeNodeId.value = null
    zoomScale.value = 1.0
    panOffset.value = { x: 0, y: 0 }
    loading.value = false
    error.value = null
  }

  return {
    // state
    nodes,
    edges,
    documentId,
    physicsEnabled,
    activeNodeId,
    zoomScale,
    panOffset,
    loading,
    error,
    // getters
    isPhysicsOn,
    hasActiveNode,
    zoomPercent,
    nodeCount,
    edgeCount,
    graphData,
    // actions
    setGraph,
    clearGraph,
    togglePhysics,
    setPhysics,
    setActiveNode,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
    setPan,
    setLoading,
    setError,
    reset,
  }
})
