import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface NodeEntity {
  id: number
  docId: number
  label: string
  summary: string | null
  positionX: number | null
  positionY: number | null
  weight: number | null
  color: string
  themeCategory: string | null
  fullText: string | null
}

export const useNodeStore = defineStore('nodes', () => {
  // ── State ──────────────────────────────────────
  const items = ref<NodeEntity[]>([])
  const activeId = ref<number | null>(null)
  const loading = ref(false)

  // ── Getters ────────────────────────────────────
  const all = computed(() => items.value)
  const count = computed(() => items.value.length)
  const active = computed(() => items.value.find((n) => n.id === activeId.value) ?? null)
  const byDocId = computed(() => (docId: number) => items.value.filter((n) => n.docId === docId))

  // ── Actions ─────────────────────────────────────
  const setAll = (nodes: NodeEntity[]) => {
    items.value = nodes
  }

  const add = (node: NodeEntity) => {
    items.value.push(node)
  }

  const remove = (id: number) => {
    const idx = items.value.findIndex((n) => n.id === id)
    if (idx !== -1) items.value.splice(idx, 1)
    if (activeId.value === id) activeId.value = null
  }

  const update = (id: number, patch: Partial<NodeEntity>) => {
    const node = items.value.find((n) => n.id === id)
    if (node) Object.assign(node, patch)
  }

  const setActive = (id: number | null) => {
    activeId.value = id
  }

  const setLoading = (v: boolean) => {
    loading.value = v
  }

  return {
    // state
    items,
    activeId,
    loading,
    // getters
    all,
    count,
    active,
    byDocId,
    // actions
    setAll,
    add,
    remove,
    update,
    setActive,
    setLoading,
  }
})
