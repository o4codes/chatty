import { ref, computed, onMounted, onUnmounted } from 'vue'

export function useCountdown(expiresAt) {
  const totalSeconds = ref(0)
  let intervalId = null

  function update() {
    const remaining = Math.max(0, new Date(expiresAt).getTime() - Date.now())
    totalSeconds.value = Math.ceil(remaining / 1000)

    if (totalSeconds.value <= 0 && intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  const minutes = computed(() => Math.floor(totalSeconds.value / 60))
  const seconds = computed(() => totalSeconds.value % 60)
  const isWarning = computed(() => totalSeconds.value <= 300 && totalSeconds.value > 60)
  const isCritical = computed(() => totalSeconds.value <= 60 && totalSeconds.value > 0)
  const isExpired = computed(() => totalSeconds.value <= 0)

  const formatted = computed(() => {
    const m = String(minutes.value).padStart(2, '0')
    const s = String(seconds.value).padStart(2, '0')
    return `${m}:${s}`
  })

  onMounted(() => {
    update()
    intervalId = setInterval(update, 1000)
  })

  onUnmounted(() => {
    if (intervalId) {
      clearInterval(intervalId)
    }
  })

  return { totalSeconds, minutes, seconds, isWarning, isCritical, isExpired, formatted }
}
