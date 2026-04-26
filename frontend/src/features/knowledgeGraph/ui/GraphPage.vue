<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">Knowledge Graph</h1>
    <p class="mt-2 text-gray-600">Document: {{ documentStore.active?.title ?? `ID ${docId}` }}</p>
    <div class="mt-6 rounded-lg border p-12 text-center text-gray-500">
      Graph visualization will render here.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { docIdParamsSchema } from '@/shared/lib/routeRecord'
import { useTypedRouter } from '@/shared/lib/useTypedRouter'

import { useDocumentStore } from '@/entities/document'

const route = useRoute()
const typedRouter = useTypedRouter()
const documentStore = useDocumentStore()

const docId = computed(() => {
  const parsed = docIdParamsSchema.safeParse(route.params)
  if (!parsed.success) {
    void typedRouter.toLibrary()
    return null
  }
  documentStore.setActive(parsed.data.docId)
  return parsed.data.docId
})

</script>
