<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRoom } from '../composables/useRoom'
import { useWebSocket } from '../composables/useWebSocket'
import CountdownTimer from '../components/CountdownTimer.vue'
import DisplayNameModal from '../components/DisplayNameModal.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import RoomExpiredOverlay from '../components/RoomExpiredOverlay.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const router = useRouter()
const { getRoom, loading } = useRoom()

// State
const room = ref(null)
const notFound = ref(false)
const displayName = ref('')
const showNameModal = ref(true)
const messages = ref([])
const isExpired = ref(false)
const connectionStatus = ref('disconnected') // 'disconnected' | 'connected' | 'reconnecting' | 'failed'
const chatContainer = ref(null)

// Session storage key for display name
const storageKey = `chatty-name-${props.id}`

// WebSocket
let ws = null

function initWebSocket() {
  ws = useWebSocket(props.id, {
    onMessage(data) {
      messages.value.push({
        id: crypto.randomUUID(),
        sender: data.sender,
        content: data.content,
        timestamp: data.timestamp,
        isSystem: false,
      })
      nextTick(scrollToBottom)
    },
    onClose(reason) {
      if (reason === 'expired') {
        isExpired.value = true
        connectionStatus.value = 'disconnected'
      } else if (reason === 'not_found') {
        notFound.value = true
        connectionStatus.value = 'disconnected'
      } else if (reason === 'failed') {
        connectionStatus.value = 'failed'
      } else {
        connectionStatus.value = 'disconnected'
      }
    },
    onError() {
      // Errors are handled in onClose
    },
  })

  // Track reconnecting state
  watch(ws.isConnected, (connected) => {
    if (connected) {
      if (connectionStatus.value === 'reconnecting') {
        addSystemMessage('Reconnected successfully')
      }
      connectionStatus.value = 'connected'
    } else if (connectionStatus.value === 'connected') {
      connectionStatus.value = 'reconnecting'
    }
  })

  ws.connect()
  connectionStatus.value = 'connected'

  // Add join system message
  addSystemMessage(`You joined as ${displayName.value}`)
}

function addSystemMessage(content) {
  messages.value.push({
    id: crypto.randomUUID(),
    sender: '__system__',
    content,
    timestamp: new Date().toISOString(),
    isSystem: true,
  })
  nextTick(scrollToBottom)
}

function handleNameSubmit(name) {
  displayName.value = name
  showNameModal.value = false
  sessionStorage.setItem(storageKey, name)
  initWebSocket()
}

function handleSend(content) {
  if (!ws) return
  ws.send({
    sender: displayName.value,
    content,
  })
}

function handleExpired() {
  isExpired.value = true
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const isOwnMessage = (sender) => sender === displayName.value

// On mount: fetch room and check for stored name
onMounted(async () => {
  const data = await getRoom(props.id)

  if (!data) {
    notFound.value = true
    return
  }

  room.value = data

  // Check for stored display name
  const storedName = sessionStorage.getItem(storageKey)
  if (storedName) {
    displayName.value = storedName
    showNameModal.value = false
    initWebSocket()
    addSystemMessage('You reconnected. Previous messages are not available.')
  }
})
</script>

<template>
  <!-- Loading state -->
  <div
    v-if="loading"
    class="flex-1 flex items-center justify-center"
  >
    <svg
      class="animate-spin w-8 h-8 text-brand"
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
  </div>

  <!-- Room not found -->
  <div
    v-else-if="notFound"
    class="flex-1 flex items-center justify-center px-4"
  >
    <div class="text-center max-w-sm">
      <div
        class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 mb-4"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-8 h-8 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
        Room not found
      </h2>
      <p class="text-gray-500 dark:text-gray-400 mb-6">
        This room may have expired or the link is invalid.
      </p>
      <button
        @click="router.push({ name: 'home' })"
        class="px-6 py-2.5 rounded-xl bg-brand hover:bg-brand-dark text-white font-medium transition-colors cursor-pointer"
      >
        Create New Room
      </button>
    </div>
  </div>

  <!-- Chat room -->
  <div v-else-if="room">
    <!-- Countdown in header area -->
    <div class="flex items-center justify-center gap-3 py-2 border-b border-gray-100 dark:border-gray-800/50 bg-gray-50/50 dark:bg-gray-900/50">
      <span class="text-xs text-gray-400 dark:text-gray-500 font-mono">{{ id }}</span>
      <CountdownTimer :expires-at="room.expires_at" @expired="handleExpired" />
    </div>

    <!-- Connection status banner -->
    <div
      v-if="connectionStatus === 'reconnecting'"
      class="px-4 py-2 text-center text-sm bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400"
    >
      <span class="inline-flex items-center gap-2">
        <svg
          class="animate-spin w-4 h-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Reconnecting...
      </span>
    </div>

    <div
      v-if="connectionStatus === 'failed'"
      class="px-4 py-2 text-center text-sm bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400"
    >
      Connection lost.
      <button
        @click="() => { location.reload() }"
        class="underline font-medium ml-1 cursor-pointer"
      >
        Refresh the page
      </button>
    </div>

    <!-- Messages area -->
    <div
      ref="chatContainer"
      class="flex-1 overflow-y-auto chat-scroll py-4 space-y-3"
    >
      <div class="max-w-3xl mx-auto space-y-3">
        <!-- Empty state -->
        <div
          v-if="messages.length === 0 && !showNameModal"
          class="flex items-center justify-center h-full min-h-[200px]"
        >
          <p class="text-sm text-gray-400 dark:text-gray-500 italic">
            No messages yet. Say something!
          </p>
        </div>

        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :sender="msg.sender"
          :content="msg.content"
          :timestamp="msg.timestamp"
          :is-own="isOwnMessage(msg.sender)"
          :is-system="msg.isSystem"
        />
      </div>
    </div>

    <!-- Chat input -->
    <ChatInput
      :disabled="connectionStatus !== 'connected' || isExpired"
      @send="handleSend"
    />

    <!-- Display name modal -->
    <DisplayNameModal
      v-if="showNameModal"
      @submit="handleNameSubmit"
    />

    <!-- Expired overlay -->
    <RoomExpiredOverlay v-if="isExpired" />
  </div>
</template>
