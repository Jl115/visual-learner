import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface QuizQuestion {
  id: number
  text: string
  options: string[]
  correctIndex: number
  explanation: string | null
}

export interface QuizSession {
  id: number
  docId: number
  nodeId: number | null
  totalQuestions: number
  questions: QuizQuestion[]
}

export const useQuizStore = defineStore('quiz', () => {
  // ── State ──────────────────────────────────────
  const session = ref<QuizSession | null>(null)
  const currentIndex = ref(0)
  const selectedAnswer = ref<number | null>(null)
  const timerSeconds = ref(0)
  const score = ref(0)
  const answered = ref<Set<number>>(new Set())
  const timerInterval = ref<ReturnType<typeof setInterval> | null>(null)

  // ── Getters ────────────────────────────────────
  const currentQuestion = computed(() => {
    if (!session.value) return null
    return session.value.questions[currentIndex.value] ?? null
  })

  const total = computed(() => session.value?.totalQuestions ?? 0)
  const isLast = computed(() => currentIndex.value === total.value - 1)
  const hasSelected = computed(() => selectedAnswer.value !== null)
  const isCorrect = computed(() => {
    const q = currentQuestion.value
    if (!q || selectedAnswer.value === null) return false
    return selectedAnswer.value === q.correctIndex
  })

  const timerDisplay = computed(() => {
    const m = Math.floor(timerSeconds.value / 60)
      .toString()
      .padStart(2, '0')
    const s = (timerSeconds.value % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  })

  // ── Actions ─────────────────────────────────────
  const startSession = (quiz: QuizSession) => {
    session.value = quiz
    currentIndex.value = 0
    selectedAnswer.value = null
    score.value = 0
    answered.value = new Set()
    startTimer()
  }

  const startTimer = () => {
    timerSeconds.value = 0
    if (timerInterval.value) clearInterval(timerInterval.value)
    timerInterval.value = setInterval(() => {
      timerSeconds.value++
    }, 1000)
  }

  const stopTimer = () => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }
  }

  const selectAnswer = (idx: number) => {
    selectedAnswer.value = idx
  }

  const submitAnswer = () => {
    const q = currentQuestion.value
    if (!q || selectedAnswer.value === null) return
    if (selectedAnswer.value === q.correctIndex) score.value++
    answered.value.add(q.id)
  }

  const next = () => {
    if (!isLast.value) {
      currentIndex.value++
      selectedAnswer.value = null
    }
  }

  const reset = () => {
    stopTimer()
    session.value = null
    currentIndex.value = 0
    selectedAnswer.value = null
    timerSeconds.value = 0
    score.value = 0
    answered.value = new Set()
  }

  return {
    // state
    session,
    currentIndex,
    selectedAnswer,
    timerSeconds,
    score,
    answered,
    // getters
    currentQuestion,
    total,
    isLast,
    hasSelected,
    isCorrect,
    timerDisplay,
    // actions
    startSession,
    selectAnswer,
    submitAnswer,
    next,
    reset,
  }
})
