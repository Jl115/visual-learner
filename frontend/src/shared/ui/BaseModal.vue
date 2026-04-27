<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')" />
        <!-- Panel -->
        <div class="relative w-full bg-bg-surface rounded-xl shadow-xl border border-bg-surface overflow-hidden"
             :style="panelStyle"
        >
          <button
            v-if="!hideClose"
            class="absolute top-3 right-3 text-text-muted hover:text-text-primary transition-colors"
            aria-label="Close"
            @click="$emit('close')"
          >
            ✕
          </button>
          <div class="p-6">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  open?: boolean
  width?: string
  hideClose?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  width: '28rem',
  hideClose: false,
})

defineEmits<{
  close: []
}>()

const panelStyle = computed(() => ({
  maxWidth: props.width,
}))
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
