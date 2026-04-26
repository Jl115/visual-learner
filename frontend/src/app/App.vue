<template>
  <div id="app" class="flex h-screen w-screen overflow-hidden">
    <Sidebar class="shrink-0" />
    <main class="flex-1 overflow-auto bg-bg-primary">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '@/widgets/Sidebar.vue'
</script>
