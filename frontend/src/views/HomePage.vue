<script setup>
import { useRouter } from 'vue-router'
import { useRoom } from '../composables/useRoom'

const router = useRouter()
const { createRoom, loading, error } = useRoom()

async function handleCreate() {
  const room = await createRoom()
  if (room) {
    router.push({ name: 'room', params: { id: room.room_id } })
  }
}
</script>

<template>
  <div class="flex-1 flex items-center justify-center px-4">
    <div class="max-w-md w-full text-center">
      <!-- Hero -->
      <div class="mb-8">
        <div
          class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand/10 dark:bg-brand/20 mb-6"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-8 h-8 text-brand dark:text-brand-light"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        </div>

        <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-3">
          Chatty
        </h1>
        <p class="text-gray-500 dark:text-gray-400 text-lg">
          Ephemeral chat rooms that self-destruct.<br />
          No accounts. No history.
        </p>
      </div>

      <!-- Feature badges -->
      <div class="flex flex-wrap justify-center gap-2 mb-8">
        <span
          class="px-3 py-1 text-sm rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
        >
          Instant Rooms
        </span>
        <span
          class="px-3 py-1 text-sm rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
        >
          No Signup
        </span>
        <span
          class="px-3 py-1 text-sm rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
        >
          Auto-Expires
        </span>
      </div>

      <!-- CTA -->
      <button
        @click="handleCreate"
        :disabled="loading"
        class="w-full sm:w-auto px-8 py-3 rounded-xl bg-brand hover:bg-brand-dark text-white font-semibold text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        <span v-if="loading" class="inline-flex items-center gap-2">
          <svg
            class="animate-spin w-5 h-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
          Creating...
        </span>
        <span v-else>Create a Room</span>
      </button>

      <!-- Error -->
      <p v-if="error" class="mt-4 text-sm text-danger">
        {{ error }}
      </p>

      <!-- Subtitle -->
      <p class="mt-4 text-sm text-gray-400 dark:text-gray-500">
        Rooms expire after 1 hour
      </p>
    </div>
  </div>
</template>
