import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // ── State ──────────────────────────────────────
  const activeRoute = ref('')
  const darkMode = ref(false)
  const toastQueue = ref<{ id: number; message: string; type: string }[]>([])
  const toastIdCounter = ref(0)

  // ── Getters ────────────────────────────────────
  const currentToast = computed(() => toastQueue.value[0] ?? null)
  const hasToast = computed(() => toastQueue.value.length > 0)

  // ── Actions ─────────────────────────────────────
  const init = () => {
    const stored = localStorage.getItem('darkMode')
    if (stored) darkMode.value = stored === 'true'
  }

  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', String(darkMode.value))
  }

  const setActiveRoute = (route: string) => {
    activeRoute.value = route
  }

  const pushToast = (message: string, type = 'info') => {
    const id = ++toastIdCounter.value
    toastQueue.value.push({ id, message, type })
    setTimeout(() => dismissToast(id), 4000)
  }

  const dismissToast = (id: number) => {
    const idx = toastQueue.value.findIndex((t) => t.id === id)
    if (idx !== -1) toastQueue.value.splice(idx, 1)
  }

  return {
    // state
    activeRoute,
    darkMode,
    toastQueue,
    // getters
    currentToast,
    hasToast,
    // actions
    init,
    toggleDarkMode,
    setActiveRoute,
    pushToast,
    dismissToast,
  }
})
