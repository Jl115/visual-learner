<template>
  <ThemeProvider>
    <AppShell>
      <template #titlebar>
        <TitleBar status="offline" />
      </template>

      <template #sidenav>
        <SideNav :items="navItems" />
      </template>

      <template #topbar>
        <div class="text-sm font-medium text-text-primary">{{ title }}</div>
      </template>

      <div class="text-text-muted text-sm">Drop a PDF to begin learning ✨</div>
    </AppShell>
  </ThemeProvider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ThemeProvider } from '@/app/providers'
import { AppShell, SideNav, TitleBar } from '@/widgets'
import type { NavItem } from '@/widgets/SideNav.vue'

const title = ref('Visual Learner')

const navItems: NavItem[] = [
  { name: 'home', label: 'Home', to: '/' },
  { name: 'library', label: 'Library', to: '/library' },
  { name: 'graph', label: 'Graph', to: '/graph' },
  { name: 'quiz', label: 'Quiz', to: '/quiz' },
  { name: 'progress', label: 'Progress', to: '/progress' },
]
</script>
