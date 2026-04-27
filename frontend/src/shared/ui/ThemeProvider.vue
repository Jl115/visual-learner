<template>
  <div class="vl-theme-provider" :class="{ 'theme--dark': true }">
    <!-- Slot allows wrapping the entire app -->
    <slot />
  </div>
</template>

<script setup lang="ts">
/**
 * ThemeProvider — injects CSS custom properties for dark theme.
 *
 * All design tokens come from @/shared/lib/designTokens.ts.
 * This component wraps the root App.vue so tokens are available globally.
 */
import { onBeforeMount } from 'vue'
import { COLORS, FONTS } from '@/shared/lib/designTokens'

onBeforeMount(() => {
  const root = document.documentElement
  if (!root.style.getPropertyValue('--vl-bg')) {
    root.style.setProperty('--vl-bg', COLORS.background)
    root.style.setProperty('--vl-bg-secondary', COLORS.secondaryBackground)
    root.style.setProperty('--vl-surface', COLORS.surface)
    root.style.setProperty('--vl-text', COLORS.text)
    root.style.setProperty('--vl-text-muted', COLORS.textMuted)
    root.style.setProperty('--vl-mint', COLORS.accentMint)
    root.style.setProperty('--vl-coral', COLORS.accentCoral)
    root.style.setProperty('--vl-teal', COLORS.accentTeal)
    root.style.setProperty('--vl-lavender', COLORS.accentLavender)
    root.style.setProperty('--vl-yellow', COLORS.accentYellow)
    root.style.setProperty('--vl-peach', COLORS.accentPeach)
    root.style.setProperty('--vl-sky', COLORS.accentSky)
    root.style.setProperty('--vl-rose', COLORS.accentRose)
    root.style.setProperty('--vl-sage', COLORS.accentSage)
    root.style.setProperty('--vl-slate', COLORS.accentSlate)
    root.style.setProperty('--vl-font-sans', FONTS.sans)
    root.style.setProperty('--vl-font-mono', FONTS.mono)
  }
})
</script>

<style scoped>
.vl-theme-provider {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: var(--vl-bg);
  color: var(--vl-text);
  font-family: var(--vl-font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
