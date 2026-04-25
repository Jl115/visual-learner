<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '../stores/app'
import axios from 'axios'

const store = useAppStore()
const isDragOver = ref(false)
const isLoading = ref(false)

async function handleDrop(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (!file || file.type !== 'application/pdf') return
  await uploadFile(file)
}

async function handleFileSelect() {
  const path: string | null = await (window as any).api.selectPDF()
  if (!path) return
  // For native file picker, we'll need a different flow
  // but we'll simulate with a Blob from reading via Electron for now
}

async function uploadFile(file: File) {
  isLoading.value = true
  const formData = new FormData()
  formData.append('file', file)
  try {
    const { data } = await axios.post('http://127.0.0.1:8000/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    store.setDocument(data)
    // Fetch graph after a brief processing moment
    setTimeout(async () => {
      const graphRes = await axios.get(`http://127.0.0.1:8000/graph/${data.id}`)
      store.setGraph(graphRes.data)
      isLoading.value = false
    }, 1200)
  } catch (err) {
    console.error('Upload failed', err)
    isLoading.value = false
  }
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ dragover: isDragOver, loading: isLoading }"
    @dragover.prevent="isDragOver = true"
    @dragleave.prevent="isDragOver = false"
    @drop.prevent="handleDrop"
  >
    <div class="dropzone-card">
      <div class="sparkle-icon" :class="{ spin: isLoading }">✨</div>
      <h2 class="title">{{ isLoading ? 'Analyzing your PDF...' : 'Drop a PDF here' }}</h2>
      <p class="subtitle">
        {{ isLoading 
           ? 'Extracting themes, building your knowledge graph...' 
           : 'We\'ll turn it into a playful interactive learning experience.' }}
      </p>
      <button class="upload-btn" @click="handleFileSelect" v-if="!isLoading">
        📂 Browse Files
      </button>
      <div class="particles" v-if="isLoading">
        <span class="dot" v-for="n in 5" :key="n" :style="{ animationDelay: `${n * 0.15}s` }"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dropzone {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-soft);
  transition: background 0.3s ease;
}
.dropzone.dragover { background: var(--color-brand-soft); }
.dropzone-card {
  text-align: center;
  padding: 56px 72px;
  background: rgba(255,255,255,0.96);
  border-radius: var(--radius-lg);
  box-shadow: 0 24px 64px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04);
  border: 2px dashed var(--color-border);
  max-width: 520px;
  transition: all 0.3s ease;
}
.dropzone.dragover .dropzone-card {
  border-color: var(--color-brand);
  transform: scale(1.02);
}
.sparkle-icon { font-size: 56px; margin-bottom: 18px; display: inline-block; }
.spin { animation: spin-bounce 1.4s ease-in-out infinite; }
@keyframes spin-bounce {
  0%, 100% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.2); }
}
.title { font-size: 26px; font-weight: 700; color: var(--color-text); margin-bottom: 10px; }
.subtitle { font-size: 15px; color: var(--color-text-secondary); margin-bottom: 28px; }
.upload-btn {
  padding: 12px 28px;
  border-radius: var(--radius-md);
  background: var(--color-brand);
  color: #fff;
  font-weight: 600;
  font-size: 15px;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.upload-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99,102,241,0.35); }
.particles { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: var(--color-brand); animation: bounce 1s infinite ease-in-out alternate; }
@keyframes bounce { to { transform: translateY(-10px); opacity: 0.5; } }
</style>
