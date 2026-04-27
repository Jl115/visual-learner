<template>
  <div class="w-full">
    <label v-if="label" :for="id" class="mb-1.5 block text-sm font-medium text-text-secondary">
      {{ label }}
    </label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full rounded-md border border-bg-surface bg-bg-secondary px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-mint focus:outline-none focus:ring-1 focus:ring-mint/40 transition-colors disabled:opacity-50"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="$emit('blur', $event)"
      @focus="$emit('focus', $event)"
    />
    <p v-if="hint" class="mt-1 text-xs text-text-muted">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  label?: string
  type?: string
  placeholder?: string
  disabled?: boolean
  hint?: string
  id?: string
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  type: 'text',
  placeholder: '',
  disabled: false,
  hint: '',
  id: () => `input-${Math.random().toString(36).slice(2, 7)}`,
})

defineEmits<{
  'update:modelValue': [value: string]
  blur: [evt: FocusEvent]
  focus: [evt: FocusEvent]
}>()
</script>
