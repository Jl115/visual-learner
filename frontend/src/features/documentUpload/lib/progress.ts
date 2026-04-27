/**
 * Pipeline progress polling composable for document processing.
 *
 * Features:
 *   - Polls GET /documents/{id}/status every 800 ms
 *   - Tracks stage / progress / error_msg
 *   - Auto-stops on completion or failure
 *   - Provides human-readable stage labels
 */
import { ref, computed } from 'vue'
import type { Ref, ComputedRef } from 'vue'

export type PipelineStage =
  | 'uploaded'
  | 'reading'
  | 'parsing'
  | 'analyzing'
  | 'graph_building'
  | 'quiz_generating'
  | 'completed'
  | 'failed'

export interface PipelineStatus {
  stage: PipelineStage
  stage_label: string
  progress: number // 0–100
  message: string
  error: string | null
}

export interface ProgressPollerResult {
  status: Ref<PipelineStatus | null>
  isPolling: ComputedRef<boolean>
  isComplete: ComputedRef<boolean>
  hasError: ComputedRef<boolean>
  start: (docId: number | string) => void
  stop: () => void
}

const POLL_INTERVAL_MS = 800
const API_BASE = 'http://localhost:8000/api/v1'

const STAGE_LABELS: Record<PipelineStage, string> = {
  uploaded: 'Uploaded – waiting to start',
  reading: 'Reading PDF',
  parsing: 'Parsing text',
  analyzing: 'Identifying themes',
  graph_building: 'Building graph',
  quiz_generating: 'Generating quizzes',
  completed: 'Complete!',
  failed: 'Failed',
}

export function useProgressPoller(): ProgressPollerResult {
  const status = ref<PipelineStatus | null>(null)
  const polling = ref(false)
  const timerId = ref<number | null>(null)

  const isPolling = computed(() => polling.value)
  const isComplete = computed(() => status.value?.stage === 'completed')
  const hasError = computed(() => status.value?.stage === 'failed' || status.value?.error !== null)

  async function fetchStatus(docId: number | string): Promise<void> {
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/status`)
      if (!res.ok) {
        if (res.status === 404) {
          // Document not found yet — keep polling
          return
        }
        throw new Error(`HTTP ${res.status}`)
      }
      const data = await res.json()
      const rawStage: string = data.stage || 'uploaded'
      const stage: PipelineStage = rawStage as PipelineStage

      status.value = {
        stage,
        stage_label: data.stage_label || STAGE_LABELS[stage] || stage,
        progress: typeof data.progress === 'number' ? data.progress : 0,
        message: data.message || '',
        error: data.error || null,
      }

      // Auto-stop when terminal
      if (stage === 'completed' || stage === 'failed') {
        stop()
      }
    } catch (err) {
      console.error('Progress poll error:', err)
    }
  }

  function start(docId: number | string): void {
    stop() // clear any existing timer
    polling.value = true
    // Immediate first fetch
    fetchStatus(docId)
    timerId.value = window.setInterval(() => {
      fetchStatus(docId)
    }, POLL_INTERVAL_MS)
  }

  function stop(): void {
    polling.value = false
    if (timerId.value !== null) {
      clearInterval(timerId.value)
      timerId.value = null
    }
  }

  return {
    status,
    isPolling,
    isComplete,
    hasError,
    start,
    stop,
  }
}
