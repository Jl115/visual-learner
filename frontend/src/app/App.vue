<template>
  <ThemeProvider>
    <router-view />
  </ThemeProvider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useAppStore } from '@/shared/lib/store'

const appStore = useAppStore()
onMounted(() => {
  appStore.init()
})
</script>

<style>
/* Global resets — keep minimal */
#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

html,
body {
  margin: 0;
  padding: 0;
  background-color: var(--vl-bg, #0f1116);
  color: var(--vl-text, #f0f0f0);
}
</style>
