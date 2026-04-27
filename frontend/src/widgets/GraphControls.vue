<template>
  <div class="flex items-center gap-3 rounded-xl bg-surface px-4 py-2 shadow-sm">
    <BaseButton variant="secondary" size="sm" @click="$emit('reset-zoom')">
      <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M4 8V6a2 2 0 012-2h2M4 16v2a2 2 0 002 2h2m8-18h2a2 2 0 012 2v2m0 8v2a2 2 0 01-2 2h-2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M15 3h6v6M9 21H3v-6M21 9v6M3 15V9" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      Reset Zoom
    </BaseButton>

    <BaseButton
      :variant="physicsEnabled ? 'primary' : 'secondary'"
      size="sm"
      @click="$emit('toggle-physics')"
    >
      <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ physicsEnabled ? 'Freeze' : 'Unfreeze' }}
    </BaseButton>

    <BaseButton variant="ghost" size="sm" @click="$emit('re-layout')">
      <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M4 4v5h.582M20.418 9l1.224-1.224a1 1 0 000-1.414l-3.536-3.536a1 1 0 00-1.414 0L15.172 4.172M9 20.418L4.172 15.172a1 1 0 010-1.414l3.536-3.536a1 1 0 011.414 0L13.172 9" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      Re-layout
    </BaseButton>

    <div class="ml-auto flex items-center gap-2 text-xs text-text-muted">
      <span>Nodes: {{ nodeCount }}</span>
      <span>Edges: {{ edgeCount }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/shared/ui/BaseButton.vue'

interface Props {
  physicsEnabled: boolean
  nodeCount: number
  edgeCount: number
}

defineProps<Props>()

defineEmits<{
  (e: 'reset-zoom'): void
  (e: 'toggle-physics'): void
  (e: 're-layout'): void
}>()
</script>
