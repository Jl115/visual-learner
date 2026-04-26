import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Badge {
  id: string
  name: string
  description: string
  icon: string
  unlockedAt: string | null
}

export interface StreakData {
  current: number
  longest: number
  lastActiveDate: string | null
}

export const useAchievementsStore = defineStore('achievements', () => {
  // ── State ──────────────────────────────────────
  const badges = ref<Badge[]>([])
  const streak = ref<StreakData>({
    current: 0,
    longest: 0,
    lastActiveDate: null,
  })
  const totalScore = ref(0)

  // ── Getters ────────────────────────────────────
  const unlockedCount = computed(() => badges.value.filter((b) => b.unlockedAt !== null).length)
  const totalBadges = computed(() => badges.value.length)
  const progressPercent = computed(() => {
    if (totalBadges.value === 0) return 0
    return Math.round((unlockedCount.value / totalBadges.value) * 100)
  })

  // ── Actions ─────────────────────────────────────
  const setBadges = (items: Badge[]) => {
    badges.value = items
  }

  const unlock = (id: string) => {
    const badge = badges.value.find((b) => b.id === id)
    if (badge && !badge.unlockedAt) {
      badge.unlockedAt = new Date().toISOString()
    }
  }

  const recordActivity = () => {
    const today = new Date().toISOString().split('T')[0]
    const last = streak.value.lastActiveDate
    if (!last) {
      streak.value.current = 1
      streak.value.longest = 1
      streak.value.lastActiveDate = today
      return
    }
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const yesterdayStr = yesterday.toISOString().split('T')[0]
    if (today === last) return // same day
    if (yesterdayStr === last) {
      streak.value.current++
      if (streak.value.current > streak.value.longest) {
        streak.value.longest = streak.value.current
      }
    } else {
      streak.value.current = 1
    }
    streak.value.lastActiveDate = today
  }

  const addScore = (points: number) => {
    totalScore.value += points
  }

  const reset = () => {
    badges.value = []
    streak.value = { current: 0, longest: 0, lastActiveDate: null }
    totalScore.value = 0
  }

  return {
    // state
    badges,
    streak,
    totalScore,
    // getters
    unlockedCount,
    totalBadges,
    progressPercent,
    // actions
    setBadges,
    unlock,
    recordActivity,
    addScore,
    reset,
  }
})
