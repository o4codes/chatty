<script setup>
import { computed } from 'vue'
import { getAvatarById } from '../data/avatars.js'

const props = defineProps({
  users: { type: Array, default: () => [] },
  query: { type: String, default: '' },
  visible: { type: Boolean, default: false },
  highlightedIndex: { type: Number, default: 0 },
})

const emit = defineEmits(['select'])

const filteredUsers = computed(() => {
  if (!props.query && props.query !== '') return props.users
  const q = props.query.toLowerCase()
  return props.users.filter(u => u.name.toLowerCase().startsWith(q))
})

const clampedIndex = computed(() =>
  Math.min(Math.max(0, props.highlightedIndex), filteredUsers.value.length - 1)
)
</script>

<template>
  <div
    v-if="visible && filteredUsers.length > 0"
    class="absolute bottom-full left-0 mb-1 w-56 max-h-48 overflow-y-auto bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-50 animate-scale-in chat-scroll"
  >
    <button
      v-for="(user, index) in filteredUsers"
      :key="user.name"
      @mousedown.prevent="emit('select', user.name)"
      class="w-full flex items-center gap-2 px-3 py-2 text-left text-sm transition-colors cursor-pointer"
      :class="index === clampedIndex
        ? 'bg-gray-100 dark:bg-gray-800'
        : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'"
    >
      <div
        v-if="user.avatar && getAvatarById(user.avatar)"
        class="w-6 h-6 rounded-full overflow-hidden shrink-0"
        v-html="getAvatarById(user.avatar).svg"
      ></div>
      <span
        v-else
        class="w-6 h-6 rounded-full bg-brand/20 text-brand text-[10px] font-bold flex items-center justify-center shrink-0"
      >
        {{ user.name.charAt(0).toUpperCase() }}
      </span>
      <span class="text-gray-700 dark:text-gray-300 truncate">{{ user.name }}</span>
    </button>
  </div>
</template>
