/**
 * IPC composable for document-upload drag-and-drop with pipeline progress
 *
 * Encapsulates:
 *   - Electron native file-drop via `window.api.readFileBuffer`
 *   - Streaming the binary to FastAPI as multipart/form-data
 *   - Pipeline progress polling via useProgressPoller
 *   - Progress / error / retry UI state
 *
 * Strict FSA / OOP alignment:
 *   - No global state; everything lives in the returned composable.
 *   - Service injected into UI; UI does not call `fs` or `fetch` directly.
 */
import { ref, computed } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { useUploadStore } from '@/features/documentUpload/model/store'
import { useProgressPoller } from '@/features/documentUpload/lib/progress'

export type UploadStatus = 'idle' | 'reading' | 'uploading' | 'processing' | 'success' | 'error'

const MAX_FILE_SIZE = 20 * 1024 * 1024 // 20 MB

export interface FileDropOptions {
  /** FastAPI upload endpoint (default: http://localhost:8000/api/v1/documents/upload) */
  endpoint?: string
  /** Maximum allowed file size in bytes */
  maxBytes?: number
}

export interface FileDropResult {
  status: Ref<UploadStatus>
  progress: Ref<number>
  stageLabel: ComputedRef<string>
  error: Ref<string | null>
  isIdle: ComputedRef<boolean>
  isUploading: ComputedRef<boolean>
  isProcessing: ComputedRef<boolean>
  hasError: ComputedRef<boolean>
  onDrop: (event: DragEvent) => Promise<void>
  reset: () => void
}

export function useFileDrop(options: FileDropOptions = {}): FileDropResult {
  const store = useUploadStore()
  const poller = useProgressPoller()

  const status = ref<UploadStatus>('idle')
  const progress = ref(0)
  const error = ref<string | null>(null)

  const endpoint = options.endpoint ?? 'http://localhost:8000/api/v1/documents/upload'
  const maxBytes = options.maxBytes ?? MAX_FILE_SIZE

  const isIdle = computed(() => status.value === 'idle')
  const isUploading = computed(() => status.value === 'uploading' || status.value === 'reading')
  const isProcessing = computed(() => status.value === 'processing')
  const hasError = computed(() => status.value === 'error' || poller.hasError.value)

  // Derive stage label from poller or fallback
  const stageLabel = computed(() => {
    if (poller.status.value?.stage_label) {
      return poller.status.value.stage_label
    }
    if (status.value === 'reading') return 'Reading PDF'
    if (status.value === 'uploading') return 'Uploading...'
    return ''
  })

  function reset() {
    status.value = 'idle'
    progress.value = 0
    error.value = null
    poller.stop()
    store.reset()
  }

  async function _readFileBuffer(file: File): Promise<Uint8Array> {
    if (file.size > maxBytes) {
      throw new Error(
        `File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max ${maxBytes / 1024 / 1024} MB.`
      )
    }
    const electronFile = file as File & { path?: string }
    const win = window as unknown as { api?: { readFileBuffer: (p: string) => Promise<Uint8Array> } }
    if (electronFile.path && win.api?.readFileBuffer) {
      return await win.api.readFileBuffer(electronFile.path)
    }
    return new Uint8Array(await file.arrayBuffer())
  }

  async function _uploadBinary(fileName: string, binary: Uint8Array): Promise<{ docId: string }> {
    const form = new FormData()
    form.append('file', new Blob([binary], { type: 'application/octet-stream' }), fileName)

    const xhr = new XMLHttpRequest()

    const docId = await new Promise<string>((resolve, reject) => {
      xhr.upload.addEventListener('progress', (evt) => {
        if (evt.lengthComputable) {
          progress.value = Math.round((evt.loaded / evt.total) * 100)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const parsed = JSON.parse(xhr.responseText)
            resolve(parsed.id ?? '')
          } catch {
            resolve('')
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.statusText || `HTTP ${xhr.status}`}`))
        }
      })

      xhr.addEventListener('error', () => reject(new Error('Network error during upload')))
      xhr.addEventListener('abort', () => reject(new Error('Upload aborted')))

      xhr.open('POST', endpoint)
      xhr.send(form)
    })

    return { docId }
  }

  async function onDrop(event: DragEvent): Promise<void> {
    event.preventDefault()
    event.stopPropagation()

    const files = event.dataTransfer?.files
    if (!files || files.length === 0) return

    const file = files[0]
    store.setFileName(file.name)
    store.setDragActive(false)

    status.value = 'reading'
    progress.value = 0
    error.value = null

    try {
      const binary = await _readFileBuffer(file)
      status.value = 'uploading'
      const { docId } = await _uploadBinary(file.name, binary)

      if (!docId) {
        throw new Error('No document ID returned from upload')
      }

      store.setDocId(docId)

      // Switch to pipeline processing phase
      status.value = 'processing'
      progress.value = 0

      // Start polling for pipeline progress
      poller.start(docId)
    } catch (err) {
      status.value = 'error'
      const msg = err instanceof Error ? err.message : String(err)
      error.value = msg
      store.setError(msg)
    }
  }

  return {
    status,
    progress,
    stageLabel,
    error,
    isIdle,
    isUploading,
    isProcessing,
    hasError,
    onDrop,
    reset,
  }
}
