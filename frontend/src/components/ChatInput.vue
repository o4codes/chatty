<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['send'])

const message = ref('')
const textareaRef = ref(null)
const maxLength = 2000

function handleSend() {
  const trimmed = message.value.trim()
  if (trimmed.length === 0 || props.disabled) return
  emit('send', trimmed)
  message.value = ''
  nextTick(resizeTextarea)
}

function handleKeydown(e) {
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
</script>

<template>
  <div
    class="shrink-0 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3"
  >
    <div class="max-w-3xl mx-auto flex items-end gap-2">
      <textarea
        ref="textareaRef"
        v-model="message"
        :maxlength="maxLength"
        :disabled="disabled"
        rows="1"
        placeholder="Type a message..."
        class="flex-1 resize-none px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors text-sm"
        @keydown="handleKeydown"
        @input="resizeTextarea"
      />
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
</template>
