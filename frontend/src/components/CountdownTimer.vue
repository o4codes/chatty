<script setup>
import { useCountdown } from '../composables/useCountdown'

const props = defineProps({
  expiresAt: { type: String, required: true },
})

const emit = defineEmits(['expired'])

const { formatted, isWarning, isCritical, isExpired } = useCountdown(props.expiresAt)

// Watch for expiration
import { watch } from 'vue'
watch(isExpired, (val) => {
  if (val) emit('expired')
})
</script>

<template>
  <div
    class="inline-flex items-center gap-1.5 text-sm font-mono"
    :class="{
      'text-gray-500 dark:text-gray-400': !isWarning && !isCritical,
      'text-warning animate-pulse': isWarning,
      'text-danger animate-pulse': isCritical,
    }"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="w-4 h-4"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
    <span>{{ formatted }}</span>
  </div>
</template>
