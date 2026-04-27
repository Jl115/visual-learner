import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as masteryApi from '../api/mastery'
import type { GraphWithStates, MasteryStats, NodeWithState } from '../api/mastery'

export const useMasteryStore = defineStore('mastery', () => {
  // ── State ──────────────────────────────────────
  const nodes = ref<NodeWithState[]>([])
  const edges = ref<{ id: number; from: number; to: number; color?: string }[]>([])
  const documentId = ref<number | null>(null)
  const stats = ref<MasteryStats | null>(null)
  const activeState = ref<NodeWithState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ── Getters ────────────────────────────────────
  const nodeCount = computed(() => nodes.value.length)
  const learnedCount = computed(() => stats.value?.learned_count ?? 0)
  const masteryPercent = computed(() => stats.value?.mastery_percent ?? 0.0)
  const stateByNodeId = computed(() => {
    const map = new Map<number, NodeWithState>()
    for (const n of nodes.value) {
      map.set(n.id, n)
    }
    return map
  })

  // ── Actions ─────────────────────────────────────
  const loadMasteryGraph = async (docId: number) => {
    loading.value = true
    error.value = null
    try {
      const payload = await masteryApi.fetchMasteryGraph(docId)
      documentId.value = payload.document_id
      nodes.value = payload.nodes
      edges.value = payload.edges
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to load mastery graph'
    } finally {
      loading.value = false
    }
  }

  const loadStats = async (docId: number) => {
    try {
      stats.value = await masteryApi.fetchMasteryStats(docId)
    } catch (err: any) {
      console.warn('mastery stats error:', err?.message)
    }
  }

  const setNodeState = async (nodeId: number, newState: 'new' | 'reviewing' | 'learned') => {
    try {
      const result = await masteryApi.updateNodeState(nodeId, newState)
      const node = nodes.value.find((n) => n.id === nodeId)
      if (node) {
        node.state = newState
        node.color = _stateColor(newState)
        node.review_count = result.review_count
        node.last_reviewed = result.last_reviewed
      }
      activeState.value = node || null
      if (documentId.value) await loadStats(documentId.value)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to update state'
    }
  }

  const recordAttempt = async (nodeId: number, score: number, total: number) => {
    try {
      const result = await masteryApi.recordNodeAttempt(nodeId, score, total)
      const node = nodes.value.find((n) => n.id === nodeId)
      if (node) {
        node.state = result.state
        node.color = _stateColor(result.state)
        node.review_count = result.review_count
        node.last_reviewed = result.last_reviewed
      }
      activeState.value = node || null
      if (documentId.value) await loadStats(documentId.value)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to record attempt'
    }
  }

  const resetNode = async (nodeId: number) => {
    try {
      const result = await masteryApi.resetNodeState(nodeId)
      const node = nodes.value.find((n) => n.id === nodeId)
      if (node) {
        node.state = 'new'
        node.color = _stateColor('new')
        node.review_count = 0
        node.last_reviewed = null
      }
      activeState.value = node || null
      if (documentId.value) await loadStats(documentId.value)
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || 'Failed to reset node'
    }
  }

  const selectNode = (nodeId: number | null) => {
    if (nodeId === null) {
      activeState.value = null
      return
    }
    activeState.value = nodes.value.find((n) => n.id === nodeId) || null
  }

  const clear = () => {
    nodes.value = []
    edges.value = []
    documentId.value = null
    stats.value = null
    activeState.value = null
    error.value = null
  }

  // ── Helpers ────────────────────────────────────
  function _stateColor(state: 'new' | 'reviewing' | 'learned'): string {
    const map: Record<string, string> = {
      new: '#DDA0DD',
      reviewing: '#FFDAB9',
      learned: '#9CAF88',
    }
    return map[state] || '#4ECDC4'
  }

  return {
    nodes,
    edges,
    documentId,
    stats,
    activeState,
    loading,
    error,
    nodeCount,
    learnedCount,
    masteryPercent,
    stateByNodeId,
    loadMasteryGraph,
    loadStats,
    setNodeState,
    recordAttempt,
    resetNode,
    selectNode,
    clear,
  }
})
