<script setup lang="ts">
import { useAppStore } from '../stores/app'
const store = useAppStore()
</script>

<template>
  <transition name="slide">
    <div v-if="store.activeNode" class="side-panel">
      <button class="close" @click="store.closePanel">✕</button>
      <div class="panel-header">
        <span class="panel-badge">{{ store.nodeCategory }}</span>
        <h3 class="panel-title">{{ store.nodeTitle }}</h3>
      </div>
      <p class="panel-summary">{{ store.nodeSummary }}</p>
      <button class="quiz-btn" @click="store.openQuiz">🎮 Take Quiz</button>
    </div>
  </transition>
</template>

<style scoped>
.side-panel {
  position: absolute;
  right: 0;
  top: 0;
  width: 340px;
  height: 100%;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(20px);
  border-left: 1px solid var(--color-border);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  z-index: 10;
}
.close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-secondary);
}
.panel-header { margin-top: 8px; }
.panel-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.panel-title { font-size: 22px; font-weight: 700; margin: 10px 0 0; }
.panel-summary { font-size: 14px; line-height: 1.65; color: var(--color-text-secondary); }
.quiz-btn {
  margin-top: auto;
  padding: 12px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.quiz-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3); }

.slide-enter-active, .slide-leave-active { transition: transform 0.35s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
