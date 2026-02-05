<script setup>
import { computed } from 'vue'
import { getAvatarById } from '../data/avatars.js'

const props = defineProps({
  id: { type: String, required: true },
  sender: { type: String, required: true },
  content: { type: String, required: true },
  timestamp: { type: String, required: true },
  isOwn: { type: Boolean, default: false },
  isSystem: { type: Boolean, default: false },
  avatar: { type: String, default: null },
  mentions: { type: Array, default: () => [] },
  replyTo: { type: Object, default: null },
})

const emit = defineEmits(['reply'])

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

// Split content into text and mention parts for highlighted rendering
const contentParts = computed(() => {
  if (!props.mentions || props.mentions.length === 0) {
    return [{ type: 'text', value: props.content }]
  }

  // Sort by name length descending to match longest names first
  const sortedNames = [...props.mentions].sort((a, b) => b.length - a.length)
  const escaped = sortedNames.map(m => m.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const regex = new RegExp(`(@(?:${escaped.join('|')}))(?=\\s|$)`, 'g')

  const parts = []
  let lastIndex = 0
  let match
  while ((match = regex.exec(props.content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: props.content.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'mention', value: match[1] })
    lastIndex = regex.lastIndex
  }
  if (lastIndex < props.content.length) {
    parts.push({ type: 'text', value: props.content.slice(lastIndex) })
  }

  return parts
})

function emitReply() {
  emit('reply', {
    id: props.id,
    sender: props.sender,
    content: props.content,
  })
}
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
    <div class="group relative max-w-[75%] sm:max-w-[65%]">
      <!-- Reply button (left side for own messages) -->
      <button
        @click="emitReply"
        class="absolute -top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm cursor-pointer z-10"
        title="Reply"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      </button>

      <div
        class="px-4 py-2 rounded-2xl rounded-br-md bg-brand dark:bg-indigo-600 text-white"
      >
        <!-- Reply quote -->
        <div
          v-if="replyTo"
          class="mb-1.5 px-2 py-1.5 rounded-lg bg-white/10 border-l-2 border-white/40"
        >
          <p class="text-[10px] font-medium text-white/70">
            {{ replyTo.sender }}
          </p>
          <p class="text-xs text-white/50 truncate">
            {{ replyTo.content }}
          </p>
        </div>

        <p class="text-sm whitespace-pre-wrap break-words">
          <template v-for="(part, i) in contentParts" :key="i">
            <span
              v-if="part.type === 'mention'"
              class="font-semibold underline decoration-white/40"
            >{{ part.value }}</span>
            <template v-else>{{ part.value }}</template>
          </template>
        </p>
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
    <div class="group relative max-w-[75%] sm:max-w-[65%]">
      <!-- Reply button (right side for others' messages) -->
      <button
        @click="emitReply"
        class="absolute -top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm cursor-pointer z-10"
        title="Reply"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
        </svg>
      </button>

      <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-0.5 ml-1">
        {{ sender }}
      </p>
      <div
        class="px-4 py-2 rounded-2xl rounded-bl-md bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
      >
        <!-- Reply quote -->
        <div
          v-if="replyTo"
          class="mb-1.5 px-2 py-1.5 rounded-lg bg-black/5 dark:bg-white/5 border-l-2 border-gray-400 dark:border-gray-500"
        >
          <p class="text-[10px] font-medium text-gray-500 dark:text-gray-400">
            {{ replyTo.sender }}
          </p>
          <p class="text-xs text-gray-400 dark:text-gray-500 truncate">
            {{ replyTo.content }}
          </p>
        </div>

        <p class="text-sm whitespace-pre-wrap break-words">
          <template v-for="(part, i) in contentParts" :key="i">
            <span
              v-if="part.type === 'mention'"
              class="font-semibold text-brand dark:text-brand-light bg-brand/10 dark:bg-brand/20 rounded px-0.5"
            >{{ part.value }}</span>
            <template v-else>{{ part.value }}</template>
          </template>
        </p>
      </div>
      <p class="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5 ml-1">
        {{ formattedTime }}
      </p>
    </div>
  </div>
</template>
