<script setup>
import { computed } from 'vue'
import { getAvatarById } from '../data/avatars.js'

const props = defineProps({
  sender: { type: String, required: true },
  content: { type: String, required: true },
  timestamp: { type: String, required: true },
  isOwn: { type: Boolean, default: false },
  isSystem: { type: Boolean, default: false },
  avatar: { type: String, default: null },
})

const avatarSvg = computed(() => {
  if (!props.avatar) return null
  const av = getAvatarById(props.avatar)
  return av ? av.svg : null
})

const formattedTime = computed(() => {
  const d = new Date(props.timestamp)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
})

// Deterministic avatar color from sender name
const avatarColor = computed(() => {
  const colors = [
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-emerald-500',
    'bg-teal-500', 'bg-cyan-500', 'bg-blue-500', 'bg-violet-500',
    'bg-purple-500', 'bg-pink-500',
  ]
  let hash = 0
  for (let i = 0; i < props.sender.length; i++) {
    hash = props.sender.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
})

const avatarLetter = computed(() => props.sender.charAt(0).toUpperCase())
</script>

<template>
  <!-- System message -->
  <div
    v-if="isSystem"
    class="animate-fade-in-up flex justify-center py-1"
  >
    <span class="text-xs italic text-gray-400 dark:text-gray-500">
      {{ content }}
    </span>
  </div>

  <!-- Own message -->
  <div
    v-else-if="isOwn"
    class="animate-fade-in-up flex justify-end gap-2 px-4"
  >
    <div class="max-w-[75%] sm:max-w-[65%]">
      <div
        class="px-4 py-2 rounded-2xl rounded-br-md bg-brand dark:bg-indigo-600 text-white"
      >
        <p class="text-sm whitespace-pre-wrap break-words">{{ content }}</p>
      </div>
      <p class="text-[10px] text-gray-400 dark:text-gray-500 text-right mt-0.5">
        {{ formattedTime }}
      </p>
    </div>
  </div>

  <!-- Others' message -->
  <div
    v-else
    class="animate-fade-in-up flex gap-2 px-4"
  >
    <div
      v-if="avatarSvg"
      class="shrink-0 w-8 h-8 rounded-full overflow-hidden mt-5"
      v-html="avatarSvg"
    ></div>
    <div
      v-else
      class="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold mt-5"
      :class="avatarColor"
    >
      {{ avatarLetter }}
    </div>
    <div class="max-w-[75%] sm:max-w-[65%]">
      <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-0.5 ml-1">
        {{ sender }}
      </p>
      <div
        class="px-4 py-2 rounded-2xl rounded-bl-md bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
      >
        <p class="text-sm whitespace-pre-wrap break-words">{{ content }}</p>
      </div>
      <p class="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5 ml-1">
        {{ formattedTime }}
      </p>
    </div>
  </div>
</template>
