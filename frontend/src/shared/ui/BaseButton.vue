<template>
  <button
    :class="[
      'inline-flex items-center justify-center rounded-lg px-4 py-2 font-sans text-sm font-medium transition-colors duration-200',
      variantClasses[variant],
      sizeClasses[size],
      { 'cursor-not-allowed opacity-50': disabled },
    ]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
type ButtonVariant = 'primary' | 'secondary' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface Props {
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
}

const {
  variant = 'primary',
  size = 'md',
  disabled = false,
} = defineProps<Props>()

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-teal text-bg-primary hover:bg-mint',
  secondary: 'bg-bg-surface text-text-primary hover:bg-bg-secondary',
  ghost: 'bg-transparent text-text-secondary hover:text-text-primary',
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
}
</script>
