import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Document {
  id: number
  title: string
  sourcePath: string
  filePath: string | null
  rawText: string | null
  status: string
  errorMsg: string | null
  createdAt: string
  updatedAt: string
}

export const useDocumentStore = defineStore('documents', () => {
  // ── State ──────────────────────────────────────
  const items = ref<Document[]>([])
  const activeId = ref<number | null>(null)
  const loading = ref(false)

  // ── Getters ────────────────────────────────────
  const all = computed(() => items.value)
  const count = computed(() => items.value.length)
  const active = computed(
    () => items.value.find((d) => d.id === activeId.value) ?? null
  )

  // ── Actions ─────────────────────────────────────
  const setAll = (docs: Document[]) => {
    items.value = docs
  }

  const add = (doc: Document) => {
    items.value.push(doc)
  }

  const remove = (id: number) => {
    const idx = items.value.findIndex((d) => d.id === id)
    if (idx !== -1) items.value.splice(idx, 1)
    if (activeId.value === id) activeId.value = null
  }

  const update = (id: number, patch: Partial<Document>) => {
    const doc = items.value.find((d) => d.id === id)
    if (doc) Object.assign(doc, patch)
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
    // actions
    setAll,
    add,
    remove,
    update,
    setActive,
    setLoading,
  }
})
