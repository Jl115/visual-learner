<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold">Achievements</h1>
    <p class="mt-2 text-gray-600">Track your streaks, badges, and progress.</p>
    <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="badge in achievementsStore.badges"
        :key="badge.id"
        class="rounded-lg border p-4"
      >
        <h3 class="font-semibold">{{ badge.name }}</h3>
        <p class="mt-1 text-sm text-gray-600">{{ badge.description }}</p>
        <span v-if="badge.unlockedAt" class="mt-2 inline-block text-xs text-green-600">
          Unlocked {{ new Date(badge.unlockedAt).toLocaleDateString() }}
        </span>
        <span v-else class="mt-2 inline-block text-xs text-gray-400">Locked</span>
      </div>
      <p v-if="achievementsStore.totalBadges === 0" class="text-gray-500">
        No badges yet. Complete quizzes and build streaks to earn them!
      </p>
    </div>
    <div class="mt-8">
      <p class="text-sm text-gray-600">Current streak: {{ achievementsStore.streak.current }}</p>
      <p class="text-sm text-gray-600">Longest streak: {{ achievementsStore.streak.longest }}</p>
      <p class="text-sm text-gray-600">Total score: {{ achievementsStore.totalScore }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAchievementsStore } from '@/features/achievements/model'

const achievementsStore = useAchievementsStore()
</script>
