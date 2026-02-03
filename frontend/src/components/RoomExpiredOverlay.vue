<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
    <div
      class="animate-scale-in w-full max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 text-center"
    >
      <!-- Hourglass icon -->
      <div
        class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 mb-4"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-8 h-8 text-danger"
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
      </div>

      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        Room Expired
      </h2>
      <p class="text-gray-500 dark:text-gray-400 mb-6">
        This chat room has reached its time limit. All messages have been deleted.
      </p>

      <button
        @click="goHome"
        class="w-full px-6 py-3 rounded-xl bg-brand hover:bg-brand-dark text-white font-semibold transition-colors cursor-pointer"
      >
        Back to Home
      </button>
    </div>
  </div>
</template>
