<template>
  <div class="flex h-screen w-screen overflow-hidden select-none bg-bg-primary text-text-primary">
    <!-- Sidebar -->
    <aside class="flex w-56 flex-col border-r border-bg-surface bg-bg-secondary">
      <slot name="titlebar" />
      <div class="flex-1 overflow-y-auto px-2 py-3">
        <slot name="sidenav" />
      </div>
      <div class="px-3 py-3 text-xs text-text-muted">
        <slot name="footer" />
      </div>
    </aside>

    <!-- Main content -->
    <main class="relative flex flex-1 flex-col">
      <header v-if="showTopBar" class="flex h-12 items-center border-b border-bg-surface px-4">
        <slot name="topbar" />
        <div class="flex-1" />
        <slot name="actions" />
      </header>

      <div class="relative flex-1 overflow-auto px-6 py-6">
        <slot />
      </div>
    </main>

    <!-- Optional drawer -->
    <aside
      v-if="drawerOpen"
      class="fixed inset-y-0 right-0 z-40 w-80 border-l border-bg-surface bg-bg-secondary shadow-2xl"
      style="margin-left: auto;"
    >
      <div class="flex h-full flex-col p-4">
        <slot name="drawer" />
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
interface Props {
  showTopBar?: boolean
  drawerOpen?: boolean
}

withDefaults(defineProps<Props>(), {
  showTopBar: true,
  drawerOpen: false,
})
</script>
