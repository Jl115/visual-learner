<script setup lang="ts">
import DropZone from './components/DropZone.vue'
import LearningGraph from './components/LearningGraph.vue'
import SidePanel from './components/SidePanel.vue'
import TitleBar from './components/TitleBar.vue'
import StatsBadge from './components/StatsBadge.vue'
import { useAppStore } from './stores/app'

const store = useAppStore()
</script>

<template>
  <div class="app-root">
    <TitleBar />
    
    <div class="main-layout">
      <!-- Sidebar -->
      <asside class="sidebar">
        <div class="brand">
          <span class="brand-icon">✨</span>
          <span class="brand-text">Learner</span>
        </div>
        <nav class="nav">
          <a class="nav-item active" href="#">🌌 Graph</a>
          <a class="nav-item" href="#">🗺 Path</a>
          <a class="nav-item" href="#">🎮 Quiz</a>
          <a class="nav-item" href="#">📚 Library</a>
        </nav>
      </aside>
      
      <!-- Canvas Area -->
      <main class="canvas-area">
        <DropZone v-if="!store.hasDocument" />
        <LearningGraph v-else />
        <SidePanel v-if="store.activeNode" />
        <StatsBadge />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-root {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Public Sans', system-ui, sans-serif;
  color: var(--color-text);
  background: var(--color-bg);
  -webkit-app-region: drag;
}
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.sidebar {
  width: 220px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(14px);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  gap: 28px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 20px;
  color: var(--color-brand);
}
.brand-icon { font-size: 24px; }
.nav { display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
}
.nav-item:hover, .nav-item.active {
  background: var(--color-brand-soft);
  color: var(--color-brand);
}
.canvas-area {
  flex: 1;
  position: relative;
  display: flex;
  overflow: hidden;
}
</style>
