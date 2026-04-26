import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGraphStore = defineStore('graph', () => {
  // ── State ──────────────────────────────────────
  const physicsEnabled = ref(true)
  const activeNodeId = ref<number | null>(null)
  const zoomScale = ref(1.0)
  const panOffset = ref({ x: 0, y: 0 })

  // ── Getters ────────────────────────────────────
  const isPhysicsOn = computed(() => physicsEnabled.value)
  const hasActiveNode = computed(() => activeNodeId.value !== null)
  const zoomPercent = computed(() => Math.round(zoomScale.value * 100))

  // ── Actions ─────────────────────────────────────
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

  const reset = () => {
    physicsEnabled.value = true
    activeNodeId.value = null
    zoomScale.value = 1.0
    panOffset.value = { x: 0, y: 0 }
  }

  return {
    // state
    physicsEnabled,
    activeNodeId,
    zoomScale,
    panOffset,
    // getters
    isPhysicsOn,
    hasActiveNode,
    zoomPercent,
    // actions
    togglePhysics,
    setPhysics,
    setActiveNode,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
    setPan,
    reset,
  }
})
