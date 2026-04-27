import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUploadStore = defineStore('upload', () => {
  // ── State ──────────────────────────────────────
  const dragActive = ref(false)
  const progress = ref(0) // 0–100
  const error = ref<string | null>(null)
  const fileName = ref('')

  // ── Getters ────────────────────────────────────
  const isUploading = computed(() => progress.value > 0 && progress.value < 100)
  const hasError = computed(() => error.value !== null)

  // ── Actions ─────────────────────────────────────
  const setDragActive = (v: boolean) => {
    dragActive.value = v
  }

  const setProgress = (v: number) => {
    progress.value = Math.max(0, Math.min(100, v))
  }

  const setError = (msg: string | null) => {
    error.value = msg
  }

  const setFileName = (name: string) => {
    fileName.value = name
  }

  const reset = () => {
    dragActive.value = false
    progress.value = 0
    error.value = null
    fileName.value = ''
  }

  return {
    // state
    dragActive,
    progress,
    error,
    fileName,
    // getters
    isUploading,
    hasError,
    // actions
    setDragActive,
    setProgress,
    setError,
    setFileName,
    reset,
  }
})
