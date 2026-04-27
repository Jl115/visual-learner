<template>
  <nav class="flex flex-col gap-1 border-r bg-gray-50 px-3 py-4 dark:bg-gray-900">
    <div class="mb-4 px-2 text-xs font-bold uppercase tracking-wider text-gray-400">
      Menu
    </div>

    <router-link
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
      active-class="bg-teal-50 text-teal-700 dark:bg-teal-900/20 dark:text-teal-300"
      :class="{ 'pointer-events-none opacity-40': item.disabled }"
    >
      <span class="inline-block h-4 w-4">{{ item.icon }}</span>
      {{ item.label }}
    </router-link>

    <div class="mt-auto border-t pt-4">
      <button
        class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
        @click="toggleTheme"
      >
        <span>{{ darkMode ? '🌙' : '☀️' }}</span>
        {{ darkMode ? 'Dark' : 'Light' }}
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'

import type { RouteRecord } from '@/shared/lib/routeRecord'

import { routeTable } from '@/app/router'

const darkMode = ref(false)
watchEffect(() => {
  darkMode.value = document.documentElement.classList.contains('dark')
})

interface NavItem {
  path: string
  label: string
  icon: string
  disabled?: boolean
}

const navItems = ref<NavItem[]>(
  routeTable
    .filter((r: RouteRecord) => !r.path.includes(':'))
    .map((r: RouteRecord) => ({
      path: r.path,
      label: r.meta.label ?? r.path,
      icon: r.meta.icon ?? '•',
      disabled: false,
    }))
)

const toggleTheme = () => {
  document.documentElement.classList.toggle('dark')
  darkMode.value = document.documentElement.classList.contains('dark')
}
</script>
