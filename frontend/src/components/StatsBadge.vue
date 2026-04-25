<script setup lang="ts">
import { useAppStore } from '../stores/app'
const store = useAppStore()
</script>

<template>
  <div class="stats">
    <div class="stat">
      <span class="stat-value">{{ store.learnedCount }}</span>
      <span class="stat-label">Learned</span>
    </div>
    <div class="stat">
      <span class="stat-value">{{ store.totalScore }}</span>
      <span class="stat-label">Points</span>
    </div>
    <div class="stat">
      <span class="stat-value">{{ store.streak }}</span>
      <span class="stat-label">Streak</span>
    </div>
  </div>
</template>

<style scoped>
.stats {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 10px;
  z-index: 5;
}
.stat {
  padding: 8px 16px;
  border-radius: var(--radius-md);
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  border: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 72px;
}
.stat-value { font-size: 20px; font-weight: 700; color: var(--color-brand); }
.stat-label { font-size: 11px; font-weight: 600; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
</style>
