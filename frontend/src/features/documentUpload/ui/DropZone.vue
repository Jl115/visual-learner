<template>
  <div
    ref="dropZoneRef"
    class="drop-zone"
    :class="{
      'drop-zone--drag': store.dragActive,
      'drop-zone--error': drop.status.value === 'error',
      'drop-zone--success': drop.status.value === 'success',
    }"
    @dragenter.prevent="onDragEnter"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop="onDrop"
  >
    <div class="drop-zone__content">
      <!-- Idle -->
      <template v-if="drop.status.value !== 'success' && drop.status.value !== 'error'">
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

      <!-- Progress -->
      <template v-if="drop.isUploading.value">
        <div class="drop-zone__progress">
          <div class="drop-zone__progress-bar" :style="{ width: drop.progress.value + '%' }" />
        </div>
        <p class="drop-zone__progress-label">{{ drop.progress.value }}%</p>
      </template>

      <!-- Error -->
      <template v-if="drop.status.value === 'error'">
        <svg class="drop-zone__icon drop-zone__icon--error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
        <p class="drop-zone__title drop-zone__title--error">Upload failed</p>
        <p class="drop-zone__hint">{{ drop.error.value }}</p>
        <button class="drop-zone__retry" @click="drop.reset">Retry</button>
      </template>

      <!-- Success -->
      <template v-if="drop.status.value === 'success'">
        <svg class="drop-zone__icon drop-zone__icon--success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <p class="drop-zone__title drop-zone__title--success">Uploaded successfully!</p>
        <button class="drop-zone__retry" @click="drop.reset">Upload another</button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUploadStore } from '@/features/documentUpload/model/store'
import { useFileDrop } from '@/features/documentUpload/lib/ipc'

const store = useUploadStore()
const drop = useFileDrop()

const dropZoneRef = ref<HTMLDivElement | null>(null)

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
}

.drop-zone__progress {
  width: 100%;
  max-width: 200px;
  height: 0.5rem;
  background-color: var(--color-surface, #f1f5f9);
  border-radius: 9999px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.drop-zone__progress-bar {
  height: 100%;
  background-color: var(--color-primary, #3b82f6);
  transition: width 0.2s ease;
}

.drop-zone__progress-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #64748b);
}

.drop-zone__retry {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background-color: var(--color-primary, #3b82f6);
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.drop-zone__retry:hover {
  opacity: 0.9;
}

.drop-zone__retry:active {
  opacity: 0.8;
}
</style>
