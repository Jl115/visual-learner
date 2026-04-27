<template>
  <div class="flex h-screen flex-col items-center justify-center p-8 text-center">
    <h1 class="text-3xl font-bold">Upload Document</h1>
    <p class="mt-2 text-gray-600">Drop a PDF, TXT, or DOCX to begin learning.</p>
    <div
      class="mt-8 flex w-full max-w-md flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-12 transition-colors"
      :class="{ 'bg-gray-50 border-teal-500': uploadStore.dragActive }"
    >
      <p class="text-gray-500">Drag & drop here or click to browse</p>
      <BaseButton class="mt-4" @click="chooseFile">Browse</BaseButton>
    </div>
    <div v-if="uploadStore.fileName" class="mt-4 text-sm text-gray-600">
      Selected: {{ uploadStore.fileName }}
    </div>
    <div v-if="uploadStore.progress > 0" class="mt-4 w-full max-w-md">
      <div class="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          class="h-full rounded-full bg-teal transition-all duration-300"
          :style="{ width: `${uploadStore.progress}%` }"
        />
      </div>
    </div>
    <p v-if="uploadStore.error" class="mt-4 text-sm text-red-500">{{ uploadStore.error }}</p>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/shared/ui/BaseButton.vue'

import { useUploadStore } from '@/features/documentUpload/model'

const uploadStore = useUploadStore()

const chooseFile = () => {
  // Placeholder: actual file-selection via Electron IPC will be wired in P2
  uploadStore.setFileName('demo-file.pdf')
  uploadStore.setProgress(100)
}
</script>
