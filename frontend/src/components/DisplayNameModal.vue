<script setup>
import { ref } from 'vue'

const emit = defineEmits(['submit'])

const name = ref('')
const maxLength = 20

function handleSubmit() {
  const trimmed = name.value.trim()
  if (trimmed.length > 0 && trimmed.length <= maxLength) {
    emit('submit', trimmed)
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
    <div
      class="animate-scale-in w-full max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6"
    >
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">
        Choose your display name
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
        This name will be visible to everyone in this room.
      </p>

      <form @submit.prevent="handleSubmit">
        <input
          v-model="name"
          type="text"
          :maxlength="maxLength"
          autofocus
          placeholder="Enter a display name..."
          class="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors"
        />

        <div class="flex items-center justify-between mt-4">
          <span class="text-xs text-gray-400 dark:text-gray-500">
            {{ name.trim().length }}/{{ maxLength }}
          </span>
          <button
            type="submit"
            :disabled="name.trim().length === 0"
            class="px-6 py-2 rounded-xl bg-brand hover:bg-brand-dark text-white font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            Join Chat
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
