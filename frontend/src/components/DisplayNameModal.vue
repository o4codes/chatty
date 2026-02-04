<script setup>
import { ref } from 'vue'
import { avatars } from '../data/avatars.js'

const emit = defineEmits(['submit'])

const name = ref('')
const maxLength = 20
const step = ref('name') // 'name' | 'avatar'

function handleNameSubmit() {
  const trimmed = name.value.trim()
  if (trimmed.length > 0 && trimmed.length <= maxLength) {
    step.value = 'avatar'
  }
}

function selectAvatar(avatarId) {
  emit('submit', { name: name.value.trim(), avatar: avatarId })
}

function skip() {
  emit('submit', { name: name.value.trim(), avatar: null })
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
    <!-- Name step -->
    <div
      v-if="step === 'name'"
      class="animate-scale-in w-full max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6"
    >
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">
        Choose your display name
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
        This name will be visible to everyone in this room.
      </p>

      <form @submit.prevent="handleNameSubmit">
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
            Next
          </button>
        </div>
      </form>
    </div>

    <!-- Avatar step -->
    <div
      v-else
      class="animate-scale-in w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6"
    >
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-1">
        Pick an avatar
      </h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-5">
        Choose a profile picture, or skip to use your initials.
      </p>

      <div class="grid grid-cols-4 gap-3 mb-5 max-h-64 overflow-y-auto chat-scroll pr-1">
        <button
          v-for="av in avatars"
          :key="av.id"
          @click="selectAvatar(av.id)"
          class="w-16 h-16 mx-auto rounded-full overflow-hidden border-2 border-transparent hover:border-brand hover:scale-110 transition-all cursor-pointer"
          v-html="av.svg"
        />
      </div>

      <div class="flex items-center justify-between">
        <button
          @click="step = 'name'"
          class="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors cursor-pointer"
        >
          Back
        </button>
        <button
          @click="skip"
          class="px-6 py-2 rounded-xl border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-medium transition-colors cursor-pointer"
        >
          Skip
        </button>
      </div>
    </div>
  </div>
</template>
