<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ShadowLevel = 'none' | 'sm' | 'md' | 'lg'
type RadiusLevel = 'none' | 'sm' | 'md' | 'lg' | 'xl'
type PaddingLevel = 'none' | 'sm' | 'md' | 'lg' | 'xl'

interface Props {
  shadow?: ShadowLevel
  rounded?: RadiusLevel
  padding?: PaddingLevel
}

const props = withDefaults(defineProps<Props>(), {
  shadow: 'md',
  rounded: 'lg',
  padding: 'md',
})

const shadowMap: Record<ShadowLevel, string> = {
  none: '',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
}

const roundedMap: Record<RadiusLevel, string> = {
  none: '',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
}

const paddingMap: Record<PaddingLevel, string> = {
  none: '',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
  xl: 'p-10',
}

const cardClasses = computed(() => {
  return [
    'bg-bg-surface border border-bg-surface',
    shadowMap[props.shadow],
    roundedMap[props.rounded],
    paddingMap[props.padding],
  ].join(' ')
})
</script>
