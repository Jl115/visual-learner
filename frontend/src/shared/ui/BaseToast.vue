<template>
  <Transition name="toast">
    <div
      v-if="open"
      class="pointer-events-auto flex items-center gap-3 rounded-lg border px-4 py-3 shadow-lg"
      :class="typeClasses"
      role="status"
      aria-live="polite"
    >
      <span class="text-sm font-medium">{{ message }}</span>
      <button
        v-if="!persistent"
        class="ml-auto text-xs opacity-70 hover:opacity-100"
        aria-label="Dismiss"
        @click="dismiss"
      >
        ✕
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ToastType = 'info' | 'success' | 'warning' | 'error'

interface Props {
  open?: boolean
  message?: string
  type?: ToastType
  persistent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  message: '',
  type: 'info',
  persistent: false,
})

const emit = defineEmits<{
  dismiss: []
}>()

const typeClasses = computed(() => {
  const map: Record<ToastType, string> = {
    info:    'bg-bg-surface border-mint/20 text-mint',
    success: 'bg-bg-surface border-sage/30 text-sage',
    warning: 'bg-bg-surface border-yellow/30 text-yellow',
    error:   'bg-bg-surface border-coral/30 text-coral',
  }
  return map[props.type]
})

const dismiss = () => emit('dismiss')
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}
</style>
