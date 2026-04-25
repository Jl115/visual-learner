<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const currentIndex = ref(0)
const selected = ref<number | null>(null)
const showResult = ref(false)
const correctCount = ref(0)

const questions = computed(() => store.nodeQuizzes || [])
const current = computed(() => questions.value[currentIndex.value])
const finished = computed(() => currentIndex.value >= questions.value.length)

function selectOption(idx: number) {
  if (showResult.value) return
  selected.value = idx
  showResult.value = true
  if (idx === current.value.correct_index) {
    correctCount.value++
    store.totalScore += 10
  }
  setTimeout(() => {
    currentIndex.value++
    selected.value = null
    showResult.value = false
    if (finished.value) {
      store.streak++
      store.learnedCount++
    }
  }, 800)
}

function closeQuiz() {
  store.closePanel()
}
</script>

<template>
  <div v-if="store.activeNode" class="quiz-overlay">
    <div class="quiz-box"
      <div class="quiz-header">
        <h3 class="quiz-title">🎮 Quiz: {{ store.nodeTitle }}</h3>
        <button class="close-btn" @click="closeQuiz">✕</button>
      </div>

      <!-- Progress bar -->
      <div v-if="!finished" class="progress">
        <div class="progress-fill" :style="{ width: `${(currentIndex / questions.length) * 100}%` }"></div>
      </div>

      <div v-if="!finished && current" class="question">
        <p class="q-text">{{ current.question }}</p>
        <div class="options">
          <button
            v-for="(opt, idx) in current.options"
            :key="idx"
            class="option"
            :class="{
              correct: showResult && idx === current.correct_index,
              wrong: showResult && idx === selected && idx !== current.correct_index,
              selected: idx === selected && !showResult,
            }"
            @click="selectOption(idx)"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <div v-else class="results">
        <div class="trophy">🏆</div>
        <h4 class="r-title">Quiz Complete!</h4>
        <p class="r-score">You scored {{ correctCount }} / {{ questions.length }}</p>
        <button class="r-btn" @click="closeQuiz">Back to Graph</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}
.quiz-box {
  width: 500px;
  max-width: 90vw;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 24px 64px rgba(0,0,0,0.12);
  padding: 32px;
  display: flex; flex-direction: column; gap: 20px;
}
.quiz-header {
  display: flex; justify-content: space-between; align-items: center;
}
.quiz-title { font-size: 18px; font-weight: 700; color: var(--color-text); }
.close-btn { width: 28px; height: 28px; border-radius: 50%; border: none; background: transparent; cursor: pointer; font-size: 16px; }
.progress { height: 6px; background: var(--color-bg); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--color-brand); border-radius: 3px; transition: width 0.3s ease; }
.q-text { font-size: 16px; font-weight: 600; line-height: 1.5; }
.options { display: flex; flex-direction: column; gap: 8px; }
.option {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 2px solid var(--color-border);
  background: var(--color-bg);
  text-align: left;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.option:hover { border-color: var(--color-brand); background: var(--color-brand-soft); }
.option.selected { border-color: var(--color-brand); background: var(--color-brand-soft); }
.option.correct { border-color: #22c55e; background: #dcfce7; }
.option.wrong { border-color: #ef4444; background: #fee2e2; }
.results { text-align: center; }
.trophy { font-size: 48px; }
.r-title { font-size: 20px; font-weight: 700; margin: 8px 0; }
.r-score { font-size: 15px; color: var(--color-text-secondary); margin-bottom: 16px; }
.r-btn {
  padding: 12px 24px;
  border-radius: var(--radius-md);
  background: var(--color-brand);
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
}
</style>
