<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import MentionDropdown from './MentionDropdown.vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  onlineUsers: { type: Array, default: () => [] },
  replyingTo: { type: Object, default: null },
})

const emit = defineEmits(['send', 'typing', 'cancelReply'])

const message = ref('')
const textareaRef = ref(null)
const maxLength = 2000
const showEmojiPicker = ref(false)
const emojiPickerRef = ref(null)
const emojiButtonRef = ref(null)
const activeCategory = ref('smileys')

// Mention dropdown state
const showMentionDropdown = ref(false)
const mentionQuery = ref('')
const mentionStartIndex = ref(-1)
const highlightedMentionIndex = ref(0)

const mentionFilteredUsers = computed(() => {
  const q = mentionQuery.value.toLowerCase()
  return props.onlineUsers.filter(u => u.name.toLowerCase().startsWith(q))
})

const emojiCategories = {
  smileys: {
    label: 'Smileys',
    icon: '😀',
    emojis: ['😀','😂','🤣','😊','😍','🥰','😘','😜','🤪','😎','🥳','🤩','😇','🤔','🫡','🤫','🤭','😏','😬','😅','😢','😭','😤','🥺','😱','🤯','🫠','😴','🤮','🤑','👻','💀','🤖','👽','🫶'],
  },
  gestures: {
    label: 'Gestures',
    icon: '👋',
    emojis: ['👋','👍','👎','👏','🙌','🤝','✌️','🤞','🤟','🤙','👌','🫰','💪','🙏','☝️','👆','👇','👈','👉','🫵','✋','🤚','🖐️','🖖','👊','✊','🤛','🤜'],
  },
  hearts: {
    label: 'Hearts',
    icon: '❤️',
    emojis: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💖','💝','💘','💗','💓','💞','💕','❣️','💔','🩷','🩵','🩶','♥️','💟'],
  },
  animals: {
    label: 'Animals',
    icon: '🐶',
    emojis: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐸','🐵','🙈','🙉','🙊','🐔','🐧','🐦','🦅','🦆','🦉','🐝','🦋','🐛','🐙','🐳','🐬','🦈','🐊','🦁','🐯','🦄'],
  },
  food: {
    label: 'Food',
    icon: '🍕',
    emojis: ['🍕','🍔','🍟','🌭','🍿','🧀','🥐','🍞','🥨','🍩','🍪','🎂','🍰','🧁','🍫','🍬','🍭','🍯','☕','🍵','🧃','🍺','🍷','🥂','🍾','🧋','🥤'],
  },
  objects: {
    label: 'Objects',
    icon: '🎉',
    emojis: ['🎉','🎊','🎈','🎁','🏆','🥇','⭐','🌟','✨','⚡','🔥','💯','🎯','🎮','🎲','🎵','🎶','🎸','🎤','📱','💻','⌨️','🖥️','📸','💡','🔑','🗝️','💰','💎'],
  },
}

function extractMentions(content) {
  const mentions = []
  // Sort by name length descending to match longest names first
  const sortedNames = props.onlineUsers
    .map(u => u.name)
    .sort((a, b) => b.length - a.length)

  for (const name of sortedNames) {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(`@${escaped}(?=\\s|$)`, 'g')
    if (regex.test(content)) {
      mentions.push(name)
    }
  }
  return [...new Set(mentions)]
}

function handleSend() {
  const trimmed = message.value.trim()
  if (trimmed.length === 0 || props.disabled) return

  const mentions = extractMentions(trimmed)
  emit('send', { content: trimmed, mentions })

  message.value = ''
  showMentionDropdown.value = false
  nextTick(resizeTextarea)
}

function handleKeydown(e) {
  // Mention dropdown keyboard navigation
  if (showMentionDropdown.value && mentionFilteredUsers.value.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      highlightedMentionIndex.value = Math.min(
        highlightedMentionIndex.value + 1,
        mentionFilteredUsers.value.length - 1
      )
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      highlightedMentionIndex.value = Math.max(0, highlightedMentionIndex.value - 1)
      return
    }
    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault()
      const user = mentionFilteredUsers.value[highlightedMentionIndex.value]
      if (user) selectMention(user.name)
      return
    }
    if (e.key === 'Escape') {
      e.preventDefault()
      showMentionDropdown.value = false
      return
    }
  }

  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function resizeTextarea() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 128) + 'px'
}

function handleInput() {
  resizeTextarea()
  if (message.value.trim().length > 0) {
    emit('typing')
  }
  detectMention()
}

function detectMention() {
  const el = textareaRef.value
  if (!el) return

  const cursorPos = el.selectionStart
  const textBeforeCursor = message.value.slice(0, cursorPos)

  const lastAtIndex = textBeforeCursor.lastIndexOf('@')

  if (lastAtIndex === -1) {
    showMentionDropdown.value = false
    return
  }

  // @ must be at start or preceded by whitespace
  if (lastAtIndex > 0 && !/\s/.test(textBeforeCursor[lastAtIndex - 1])) {
    showMentionDropdown.value = false
    return
  }

  const query = textBeforeCursor.slice(lastAtIndex + 1)

  // Dismiss if query contains a newline
  if (query.includes('\n')) {
    showMentionDropdown.value = false
    return
  }

  mentionQuery.value = query
  mentionStartIndex.value = lastAtIndex
  highlightedMentionIndex.value = 0
  showMentionDropdown.value = true
}

function selectMention(username) {
  const el = textareaRef.value
  if (!el) return

  const before = message.value.slice(0, mentionStartIndex.value)
  const after = message.value.slice(el.selectionStart)
  message.value = before + '@' + username + ' ' + after
  showMentionDropdown.value = false

  nextTick(() => {
    const pos = mentionStartIndex.value + username.length + 2
    el.selectionStart = pos
    el.selectionEnd = pos
    el.focus()
    resizeTextarea()
  })
}

function toggleEmojiPicker() {
  showEmojiPicker.value = !showEmojiPicker.value
}

function insertEmoji(emoji) {
  const el = textareaRef.value
  if (!el) return

  const start = el.selectionStart
  const end = el.selectionEnd
  const before = message.value.slice(0, start)
  const after = message.value.slice(end)

  message.value = before + emoji + after
  showEmojiPicker.value = false

  nextTick(() => {
    const pos = start + emoji.length
    el.selectionStart = pos
    el.selectionEnd = pos
    el.focus()
    resizeTextarea()
  })
}

function handleClickOutside(e) {
  if (
    showEmojiPicker.value &&
    emojiPickerRef.value &&
    !emojiPickerRef.value.contains(e.target) &&
    emojiButtonRef.value &&
    !emojiButtonRef.value.contains(e.target)
  ) {
    showEmojiPicker.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<template>
  <div
    class="shrink-0 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3"
  >
    <div class="max-w-3xl mx-auto">
      <!-- Reply preview bar -->
      <div
        v-if="replyingTo"
        class="mb-2 flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-xl border-l-4 border-brand"
      >
        <div class="flex-1 min-w-0">
          <p class="text-xs font-medium text-brand dark:text-brand-light">
            Replying to {{ replyingTo.sender }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
            {{ replyingTo.content }}
          </p>
        </div>
        <button
          @click="$emit('cancelReply')"
          class="shrink-0 p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex items-end gap-2">
        <!-- Textarea with mention dropdown -->
        <div class="relative flex-1">
          <textarea
            ref="textareaRef"
            v-model="message"
            :maxlength="maxLength"
            :disabled="disabled"
            rows="1"
            placeholder="Type a message..."
            class="w-full resize-none px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors text-sm"
            @keydown="handleKeydown"
            @input="handleInput"
          />

          <MentionDropdown
            :users="onlineUsers"
            :query="mentionQuery"
            :visible="showMentionDropdown"
            :highlighted-index="highlightedMentionIndex"
            @select="selectMention"
          />
        </div>

        <!-- Emoji picker button -->
        <div class="relative">
          <button
            ref="emojiButtonRef"
            @click="toggleEmojiPicker"
            :disabled="disabled"
            class="shrink-0 w-10 h-10 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            title="Add emoji"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <!-- Emoji picker popover -->
          <div
            v-if="showEmojiPicker"
            ref="emojiPickerRef"
            class="absolute bottom-12 right-0 w-72 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-50 animate-scale-in"
          >
            <!-- Category tabs -->
            <div class="flex border-b border-gray-200 dark:border-gray-700 px-1 pt-1">
              <button
                v-for="(cat, key) in emojiCategories"
                :key="key"
                @click="activeCategory = key"
                class="flex-1 py-1.5 text-center text-base rounded-t-lg transition-colors cursor-pointer"
                :class="activeCategory === key ? 'bg-gray-100 dark:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'"
                :title="cat.label"
              >
                {{ cat.icon }}
              </button>
            </div>

            <!-- Emoji grid -->
            <div class="p-2 h-48 overflow-y-auto chat-scroll">
              <div class="grid grid-cols-8 gap-0.5">
                <button
                  v-for="emoji in emojiCategories[activeCategory].emojis"
                  :key="emoji"
                  @click="insertEmoji(emoji)"
                  class="w-8 h-8 flex items-center justify-center text-lg rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  {{ emoji }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <button
          @click="handleSend"
          :disabled="message.trim().length === 0 || disabled"
          class="shrink-0 w-10 h-10 rounded-xl bg-brand hover:bg-brand-dark text-white flex items-center justify-center transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
        >
          <svg
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
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
