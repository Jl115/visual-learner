import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const darkMode = ref(false)
  const toast = ref<{ message: string; type: string } | null>(null)

  const init = () => {
    const stored = localStorage.getItem('darkMode')
    if (stored) darkMode.value = stored === 'true'
  }

  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', String(darkMode.value))
  }

  const showToast = (message: string, type = 'info') => {
    toast.value = { message, type }
    setTimeout(() => { toast.value = null }, 3000)
  }

  return { darkMode, toast, init, toggleDarkMode, showToast }
})
