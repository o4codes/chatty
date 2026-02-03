import { ref, computed, onMounted, onUnmounted } from 'vue'

const STORAGE_KEY = 'chatty-theme'

const theme = ref('light')
const isDark = computed(() => theme.value === 'dark')
let mediaQuery = null
let manualOverride = false

function applyTheme(value) {
  theme.value = value
  document.documentElement.classList.toggle('dark', value === 'dark')
}

function handleSystemChange(e) {
  if (!manualOverride) {
    applyTheme(e.matches ? 'dark' : 'light')
  }
}

export function useTheme() {
  onMounted(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    if (stored === 'dark' || stored === 'light') {
      manualOverride = true
      applyTheme(stored)
    } else {
      applyTheme(mediaQuery.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleSystemChange)
  })

  onUnmounted(() => {
    if (mediaQuery) {
      mediaQuery.removeEventListener('change', handleSystemChange)
    }
  })

  function toggle() {
    manualOverride = true
    const next = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem(STORAGE_KEY, next)
    applyTheme(next)
  }

  return { theme, isDark, toggle }
}
