<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useAppStore } from '@/shared/lib/store'

const appStore = useAppStore()
onMounted(() => {
  appStore.init()
})
</script>
