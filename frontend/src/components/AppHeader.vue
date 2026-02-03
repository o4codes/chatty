<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '../composables/useTheme'

const route = useRoute()
const { isDark, toggle } = useTheme()

const copied = ref(false)

function copyRoomLink() {
  const url = window.location.href
  navigator.clipboard.writeText(url).then(() => {
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  })
}
</script>

<template>
  <header
    class="h-14 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shrink-0"
  >
    <!-- Logo -->
    <router-link
      to="/"
      class="text-lg font-bold text-brand dark:text-brand-light tracking-tight"
    >
      Chatty
    </router-link>

    <!-- Room info (only on room page) -->
    <div
      v-if="route.name === 'room'"
      class="flex items-center gap-3"
    >
      <button
        class="relative px-3 py-1 text-xs font-mono rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer"
        @click="copyRoomLink"
        :title="copied ? 'Copied!' : 'Copy room link'"
      >
        {{ route.params.id }}
        <span
          v-if="copied"
          class="absolute -bottom-7 left-1/2 -translate-x-1/2 px-2 py-0.5 text-[10px] rounded bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 whitespace-nowrap"
        >
          Copied!
        </span>
      </button>
    </div>

    <!-- Theme toggle -->
    <button
      @click="toggle"
      class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-500 dark:text-gray-400 cursor-pointer"
      :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <!-- Sun icon (shown in dark mode) -->
      <svg
        v-if="isDark"
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M12 3v1m0 16v1m8.66-13.66l-.71.71M4.05 19.95l-.71.71M21 12h-1M4 12H3m16.66 7.66l-.71-.71M4.05 4.05l-.71-.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"
        />
      </svg>
      <!-- Moon icon (shown in light mode) -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        class="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
        />
      </svg>
    </button>
  </header>
</template>
