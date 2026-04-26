<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">Quiz Session</h1>
    <p class="mt-2 text-gray-600">Node: {{ nodeStore.active?.label ?? `ID ${nodeId}` }}</p>
    <div class="mt-6 rounded-lg border p-12 text-center text-gray-500">
      Quiz questions will appear here.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { nodeIdParamsSchema } from '@/shared/lib/routeRecord'
import { useTypedRouter } from '@/shared/lib/useTypedRouter'

import { useNodeStore } from '@/entities/node'

const route = useRoute()
const typedRouter = useTypedRouter()
const nodeStore = useNodeStore()

const nodeId = computed(() => {
  const parsed = nodeIdParamsSchema.safeParse(route.params)
  if (!parsed.success) {
    void typedRouter.toLibrary()
    return null
  }
  nodeStore.setActive(parsed.data.nodeId)
  return parsed.data.nodeId
})

</script>
