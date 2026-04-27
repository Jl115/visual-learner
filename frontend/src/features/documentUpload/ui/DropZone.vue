<template>
  <div
    ref="dropZoneRef"
    class="drop-zone"
    :class="computedClasses"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop="onDrop"
  >
    <div class="drop-zone__content">
      <!-- Idle / Drag -->
      <template v-if="isIdle">
        <svg class="drop-zone__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        <p class="drop-zone__title">
          {{ store.fileName ? store.fileName : 'Drop a PDF here to begin learning' }}
        </p>
        <p class="drop-zone__hint">Supported: PDF, TXT, MD, DOCX</p>
      </template>

      <!-- Uploading -->
      <template v-else-if="isUploading">
        <div class="drop-zone__progress">
          <div class="drop-zone__progress-track">
            <div class="drop-zone__progress-bar" :style="{ width: drop.progress.value + '%' }" />
          </div>
        </div>
        <p class="drop-zone__progress-label">{{ drop.progress.value }}% – Uploading file</p>
      </template>

      <!-- Pipeline Processing -->
      <template v-else-if="isProcessing">
        <div class="drop-zone__stage">
          <div class="drop-zone__spinner" />
          <p class="drop-zone__stage-label">{{ drop.stageLabel.value }}</p>
        </div>
        <div class="drop-zone__progress">
          <div class="drop-zone__progress-track">
            <div class="drop-zone__progress-bar" :style="{ width: pipelineProgress + '%' }" />
          </div>
        </div>
        <p class="drop-zone__progress-label">{{ pipelineProgress }}% – {{ drop.stageLabel.value }}</p>
      </template>

      <!-- Success / Complete -->
      <template v-else-if="isComplete">
        <svg class="drop-zone__icon drop-zone__icon--success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <p class="drop-zone__title drop-zone__title--success">Uploaded successfully!</p>
        <p class="drop-zone__hint">Your knowledge graph is ready.</p>
        <button class="drop-zone__retry" @click="drop.reset">Upload another</button>
      </template>

      <!-- Error -->
      <template v-else-if="isError">
        <svg class="drop-zone__icon drop-zone__icon--error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <p class="drop-zone__title drop-zone__title--error">Processing failed</p>
        <p class="drop-zone__hint">{{ store.error || drop.error.value }}</p>
        <button v-if="store.docId" class="drop-zone__retry" @click="retryPipeline">Retry</button>
        <button v-else class="drop-zone__retry" @click="drop.reset">Try again</button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUploadStore } from '@/features/documentUpload/model/store'
import { useFileDrop } from '@/features/documentUpload/lib/ipc'
import { useProgressPoller } from '@/features/documentUpload/lib/progress'

const store = useUploadStore()
const drop = useFileDrop()
const poller = useProgressPoller()

const dropZoneRef = ref<HTMLDivElement | null>(null)

// ── Computed appearance ─────────────────────────────

const isIdle = computed(() => drop.isIdle.value && !store.dragActive)
const isActiveDrag = computed(() => !drop.isUploading.value && !drop.isProcessing.value && !drop.hasError.value &> store.dragActive)
const isUploading = computed(() => drop.isUploading.value)
const isProcessing = computed(() => drop.isProcessing.value)
const isComplete = computed(() => drop.status.value === 'success' || poller.isComplete.value)
const isError = computed(() => drop.hasError.value || (poller.status.value?.stage === 'failed'))

const pipelineProgress = computed(() => {
  const p = poller.status.value?.progress
  return p !== undefined && p !== null ? Math.round(p) : 0
})

const computedClasses = computed(() => ({
  'drop-zone--drag': isActiveDrag.value,
  'drop-zone--error': isError.value,
  'drop-zone--success': isComplete.value,
}))

// ── Drag handlers ─────────────────────────────────────

function onDragEnter(event: DragEvent) {
  event.preventDefault()
  store.setDragActive(true)
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  store.setDragActive(true)
}

function onDragLeave(event: DragEvent) {
  event.preventDefault()
  const rect = dropZoneRef.value?.getBoundingClientRect()
  if (!rect) return
  const { clientX, clientY } = event
  if (
    clientX < rect.left ||
    clientX >= rect.right ||
    clientY < rect.top ||
    clientY >= rect.bottom
  ) {
    store.setDragActive(false)
  }
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  store.setDragActive(false)
  drop.onDrop(event)
}

function retryPipeline() {
  if (store.docId) {
    drop.reset()
    poller.start(store.docId)
    // Re-trigger from beginning
    drop.status.value = 'processing'
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--color-border, #cbd5e1);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  cursor: pointer;
}

.drop-zone--drag {
  border-color: var(--color-primary, #3b82f6);
  background-color: var(--color-primary-subtle, #eff6ff);
}

.drop-zone--error {
  border-color: var(--color-error, #ef4444);
  background-color: var(--color-error-subtle, #fef2f2);
}

.drop-zone--success {
  border-color: var(--color-success, #22c55e);
  background-color: var(--color-success-subtle, #f0fdf4);
}

.drop-zone__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  min-height: 120px;
  justify-content: center;
}

.drop-zone__icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-text-secondary, #64748b);
}

.drop-zone__icon--error {
  color: var(--color-error, #ef4444);
}

.drop-zone__icon--success {
  color: var(--color-success, #22c55e);
}

.drop-zone__title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text-primary, #1e293b);
  margin: 0;
}

.drop-zone__title--error {
  color: var(--color-error, #ef4444);
}

.drop-zone__title--success {
  color: var(--color-success, #22c55e);
}

.drop-zone__hint {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0;
}

/* Upload / pipeline progress */
.drop-zone__progress {
  width: 100%;
  max-width: 220px;
}

.drop-zone__progress-track {
  width: 100%;
  height: 0.5rem;
  background-color: var(--color-surface, #f1f5f9);
  border-radius: 9999px;
  overflow: hidden;
}

.drop-zone__progress-bar {
  height: 100%;
  background-color: var(--color-primary, #3b82f6);
  transition: width 0.3s ease;
  border-radius: 9999px;
}

.drop-zone__progress-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
  margin: 0.25rem 0 0;
}

/* Pipeline stage */
.drop-zone__stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.drop-zone__spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-surface, #f1f5f9);
  border-top-color: var(--color-primary, #3b82f6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.drop-zone__stage-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary, #1e293b);
  margin: 0;
}

/* Retry button */
.drop-zone__retry {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  font-weight: 500;
  cursor: pointer;
  font-size: 0.875rem;
  transition: opacity 0.2s ease;
}

.drop-zone__retry:hover {
  opacity: 0.9;
}

.drop-zone__retry:active {
  opacity: 0.8;
}
</style>
