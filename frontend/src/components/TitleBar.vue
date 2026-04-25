<script setup lang="ts">
const minimize = () => (window as any).api.minimizeWindow()
const maximize = () => (window as any).api.maximizeWindow()
const close = () => (window as any).api.closeWindow()
</script>

<template>
  <div class="titlebar">
    <div class="brand-mini">
      <span class="icon">✨</span> Visual Learner
    </div>
    <div class="window-controls">
      <button class="win-btn minimize" @click="minimize">&minus;</button>
      <button class="win-btn maximize" @click="maximize">⬚</button>
      <button class="win-btn close" @click="close">✕</button>
    </div>
  </div>
</template>

<style scoped>
.titlebar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px 0 0;
  height: 36px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  -webkit-app-region: drag;
  user-select: none;
}
.brand-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 16px;
  font-weight: 700;
  font-size: 13px;
  color: var(--color-brand);
  -webkit-app-region: drag;
}
.icon { font-size: 15px; }
.window-controls { display: flex; gap: 6px; -webkit-app-region: no-drag; }
.win-btn {
  width: 28px; height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}
.win-btn:hover { background: var(--color-bg-soft); }
.win-btn.close:hover { background: #ff6b6b; color: #fff; }
</style>
