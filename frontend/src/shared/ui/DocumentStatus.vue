<template>
  <div class="flex w-full flex-col gap-2">
    <!-- Status badge -->
    <div class="flex items-center gap-3">
      <span
        :class="[
          'inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset',
          badgeClasses,
        ]"
      >
        <span
          class="mr-1.5 inline-block h-1.5 w-1.5 rounded-full"
          :style="{ backgroundColor: dotColor }"
        />
        {{ meta.label }}
      </span>
      <span class="text-text-muted text-xs">
        {{ Math.round(displayProgress * 100) }}%
      </span>
    </div>

    <!-- Progress bar -->
    <div class="bg-surface h-2 w-full overflow-hidden rounded-full">
      <div
        class="h-full rounded-full transition-all duration-300 ease-out"
        :class="barColorClass"
        :style="{ width: `${displayProgress * 100}%` }"
      />
    </div>

    <!-- Error message -->
    <p v-if="errorMsg" class="text-accent-coral text-xs">
      {{ errorMsg }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { DocumentState, getStateMeta } from '../lib/types'

interface Props {
  state: DocumentState | string
  progress?: number
  errorMsg?: string
}

const { state, progress = 0, errorMsg } = defineProps<Props>()

const resolvedState = computed(() => {
  if (typeof state === 'string') {
    return (Object.values(DocumentState) as string[]).includes(state)
      ? (state as DocumentState)
      : DocumentState.UPLOADED
  }
  return state || DocumentState.UPLOADED
})

const meta = computed(() => getStateMeta(resolvedState.value))

const displayProgress = computed(() => {
  const clamped = Math.max(0, Math.min(1, progress))
  return clamped
})

const dotColor = computed(() => meta.value.color)

const badgeClasses = computed(() => {
  switch (resolvedState.value) {
    case DocumentState.UPLOADED:
      return 'ring-text-muted/20 bg-surface text-text-muted'
    case DocumentState.READING:
      return 'ring-accent-sky/20 bg-accent-sky/10 text-accent-sky'
    case DocumentState.PARSING:
    case DocumentState.ANALYZING:
      return 'ring-accent-yellow/20 bg-accent-yellow/10 text-accent-yellow'
    case DocumentState.GRAPH_BUILDING:
      return 'ring-accent-teal/20 bg-accent-teal/10 text-accent-teal'
    case DocumentState.QUIZ_GENERATING:
      return 'ring-accent-lavender/20 bg-accent-lavender/10 text-accent-lavender'
    case DocumentState.COMPLETED:
      return 'ring-accent-mint/20 bg-accent-mint/10 text-accent-mint'
    case DocumentState.FAILED:
      return 'ring-accent-coral/20 bg-accent-coral/10 text-accent-coral'
    default:
      return 'ring-text-muted/20 bg-surface text-text-muted'
  }
})

const barColorClass = computed(() => {
  switch (resolvedState.value) {
    case DocumentState.FAILED:
      return 'bg-accent-coral'
    case DocumentState.COMPLETED:
      return 'bg-accent-mint'
    case DocumentState.UPLOADED:
      return 'bg-text-muted'
    default:
      return 'bg-accent-sky'
  }
})
</script>
