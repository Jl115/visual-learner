<template>
  <div
    class="draggable flex h-10 w-full items-center justify-between border-b border-bg-surface bg-bg-secondary px-4"
    style="-webkit-app-region: drag"
  >
    <div class="flex items-center gap-2 text-xs font-medium text-text-muted" style="-webkit-app-region: no-drag">
      <span class="relative flex h-3 w-3">
        <span class="absolute inline-flex h-full w-full animate-ping rounded-full opacity-75" :class="dotColor" />
        <span class="relative inline-flex h-3 w-3 rounded-full" :class="dotColor" />
      </span>
      {{ title }}
    </div>

    <div class="flex items-center gap-2" style="-webkit-app-region: no-drag">
      <button
        v-for="a in windowActions"
        :key="a.action"
        class="h-5 w-5 rounded-full transition-transform hover:scale-110 focus:outline-none"
        :class="a.color"
        :title="a.title"
        @click="a.handler?.($event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  status?: 'online' | 'offline' | 'busy' | 'idle'
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Visual Learner',
  status: 'offline',
})

const dotColor = computed(() => {
  const map: Record<NonNullable<Props['status']>, string> = {
    online: 'bg-sage',
    offline: 'bg-text-muted',
    busy: 'bg-coral',
    idle: 'bg-yellow',
  }
  return map[props.status] ?? map.offline
})

const windowActions = computed(() => [
  {
    action: 'min',
    color: 'bg-yellow',
    title: 'Minimize',
    handler: (_e: MouseEvent) => (window as any).ipcBridge?.send?.('window-minimize'),
  },
  {
    action: 'max',
    color: 'bg-sage',
    title: 'Maximize',
    handler: (_e: MouseEvent) => (window as any).ipcBridge?.send?.('window-maximize'),
  },
  {
    action: 'close',
    color: 'bg-coral',
    title: 'Close',
    handler: (_e: MouseEvent) => (window as any).ipcBridge?.send?.('window-close'),
  },
])

// NOTE: we reference window.ipcBridge which is exposed via the preload script
// In non-Electron environments this simply no-ops.
</script>
