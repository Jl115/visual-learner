<template>
  <nav class="flex flex-col gap-1">
    <RouterLink
      v-for="item in items"
      :key="item.name"
      :to="item.to"
      :class="linkClasses(item)"
      active-class="bg-mint/10 text-mint font-medium"
    >
      {{ item.label }}
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export interface NavItem {
  name: string
  label: string
  to: string
}

interface Props {
  items: NavItem[]
}

const props = defineProps<Props>()
const route = useRoute()

const linkClasses = (item: NavItem) => {
  const isActive = route.path === item.to
  return [
    'flex items-center rounded-md px-3 py-2 text-sm transition-colors',
    isActive
      ? 'bg-mint/10 text-mint font-medium'
      : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary',
  ]
}
</script>
