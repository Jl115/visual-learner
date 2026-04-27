<template>
  <div class="flex h-screen flex-col">
    <aside class="w-60 border-r border-gray-200 p-4">
      <h2 class="text-lg font-semibold">Library</h2>
      <ul class="mt-4 space-y-2">
        <li
          v-for="doc in documentStore.all"
          :key="doc.id"
          class="cursor-pointer rounded px-3 py-2 transition hover:bg-gray-100"
          :class="{ 'bg-blue-100 font-medium': activeDocId === doc.id }"
          @click="selectDoc(doc.id)"
        >
          {{ doc.title }}
        </li>
        <li v-if="documentStore.count === 0" class="text-sm text-gray-500">
          No documents yet — drop a file to start.
        </li>
      </ul>
      <div class="mt-6">
        <BaseButton @click="router.push('/upload')">Upload</BaseButton>
      </div>
    </aside>
    <main class="flex-1 p-8">
      <h1 class="text-2xl font-bold">Document Library</h1>
      <p class="mt-2 text-gray-600">Select a document to explore its graph, quiz, or learning path.</p>
      <div v-if="activeDocId" class="mt-6 flex gap-4">
        <BaseButton @click="router.push(`/graph/${activeDocId}`)">View Graph</BaseButton>
        <BaseButton @click="router.push(`/path/${activeDocId}`)">Learning Path</BaseButton>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useAppRouter } from '@/shared/lib/router'
import BaseButton from '@/shared/ui/BaseButton.vue'

import { useDocumentStore } from '@/entities/document'

const router = useAppRouter().router
const documentStore = useDocumentStore()

const activeDocId = computed(() => documentStore.activeId)

const selectDoc = (id: number) => {
  documentStore.setActive(id)
}
</script>
