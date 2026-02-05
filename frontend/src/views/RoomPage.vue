<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRoom } from '../composables/useRoom'
import { useWebSocket } from '../composables/useWebSocket'
import { getAvatarById } from '../data/avatars.js'
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
const userAvatar = ref(null)
const showNameModal = ref(true)
const messages = ref([])
const isExpired = ref(false)
const connectionStatus = ref('disconnected') // 'disconnected' | 'connected' | 'reconnecting' | 'failed'
const chatContainer = ref(null)
const linkCopied = ref(false)
const onlineUsers = ref([])
const showUsersPanel = ref(false)
const typingUsers = ref(new Set())
const typingTimers = {}

function handleTypingIndicator(userName) {
  typingUsers.value.add(userName)
  typingUsers.value = new Set(typingUsers.value) // trigger reactivity

  if (typingTimers[userName]) clearTimeout(typingTimers[userName])
  typingTimers[userName] = setTimeout(() => {
    typingUsers.value.delete(userName)
    typingUsers.value = new Set(typingUsers.value)
    delete typingTimers[userName]
  }, 3000)
}

const typingText = computed(() => {
  const users = [...typingUsers.value]
  if (users.length === 0) return ''
  if (users.length === 1) return `${users[0]} is typing...`
  if (users.length === 2) return `${users[0]} and ${users[1]} are typing...`
  return `${users[0]} and ${users.length - 1} others are typing...`
})

const roomLink = computed(() => window.location.origin + `/room/${props.id}`)

function copyRoomLink() {
  navigator.clipboard.writeText(roomLink.value).then(() => {
    linkCopied.value = true
    setTimeout(() => (linkCopied.value = false), 2000)
  })
}

// Session storage keys
const storageKey = `chatty-name-${props.id}`
const avatarStorageKey = `chatty-avatar-${props.id}`

// WebSocket
let ws = null

function initWebSocket() {
  ws = useWebSocket(props.id, displayName.value, userAvatar.value, {
    onMessage(data) {
      if (data.sender === '__user_list__') {
        onlineUsers.value = data.content
        return
      }
      if (data.sender === '__typing__') {
        handleTypingIndicator(data.content)
        return
      }
      if (data.sender === '__system__') {
        addSystemMessage(data.content)
        return
      }
      messages.value.push({
        id: crypto.randomUUID(),
        sender: data.sender,
        avatar: data.avatar || null,
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

function handleNameSubmit({ name, avatar }) {
  displayName.value = name
  userAvatar.value = avatar
  showNameModal.value = false
  sessionStorage.setItem(storageKey, name)
  if (avatar) {
    sessionStorage.setItem(avatarStorageKey, avatar)
  }
  initWebSocket()
}

function handleSend(content) {
  if (!ws) return
  ws.send({
    sender: displayName.value,
    avatar: userAvatar.value,
    content,
  })
}

function handleTyping() {
  if (!ws) return
  ws.sendTyping()
}

function handleExpired() {
  isExpired.value = true
}

function handleLeave() {
  if (ws) ws.close()
  sessionStorage.removeItem(storageKey)
  sessionStorage.removeItem(avatarStorageKey)
  router.push({ name: 'home' })
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

  // Check for stored display name and avatar
  const storedName = sessionStorage.getItem(storageKey)
  if (storedName) {
    displayName.value = storedName
    userAvatar.value = sessionStorage.getItem(avatarStorageKey) || null
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
  <div v-else-if="room" class="flex-1 flex flex-col min-h-0">
    <!-- Countdown in header area -->
    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-100 dark:border-gray-800/50 bg-gray-50/50 dark:bg-gray-900/50">
      <div class="flex items-center gap-3">
        <span class="text-xs text-gray-400 dark:text-gray-500 font-mono">{{ id }}</span>
        <CountdownTimer :expires-at="room.expires_at" @expired="handleExpired" />
      </div>
      <button
        @click="handleLeave"
        class="px-3 py-1 text-xs font-medium rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors cursor-pointer"
      >
        Leave
      </button>
    </div>

    <!-- Share link banner -->
    <div class="flex items-center justify-center gap-2 px-4 py-1.5 border-b border-gray-100 dark:border-gray-800/50 bg-gray-50/30 dark:bg-gray-900/30">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101" />
        <path stroke-linecap="round" stroke-linejoin="round" d="M10.172 13.828a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.102 1.101" />
      </svg>
      <span class="text-xs text-gray-500 dark:text-gray-400 truncate font-mono">{{ roomLink }}</span>
      <button
        @click="copyRoomLink"
        class="shrink-0 p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer"
        :title="linkCopied ? 'Copied!' : 'Copy link'"
      >
        <svg v-if="!linkCopied" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </button>
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

    <!-- Main chat area with optional users sidebar -->
    <div class="flex-1 flex min-h-0">
      <!-- Messages column -->
      <div class="flex-1 flex flex-col min-w-0 min-h-0">
        <!-- Messages area -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto chat-scroll py-4 space-y-3"
        >
          <div class="max-w-3xl mx-auto space-y-3 px-4">
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
              :avatar="msg.avatar"
              :content="msg.content"
              :timestamp="msg.timestamp"
              :is-own="isOwnMessage(msg.sender)"
              :is-system="msg.isSystem"
            />
          </div>
        </div>

        <!-- Typing indicator -->
        <div
          v-if="typingText"
          class="shrink-0 px-4 py-1"
        >
          <div class="max-w-3xl mx-auto">
            <span class="text-xs text-gray-400 dark:text-gray-500 italic animate-pulse">
              {{ typingText }}
            </span>
          </div>
        </div>

        <!-- Chat input -->
        <ChatInput
          :disabled="connectionStatus !== 'connected' || isExpired"
          @send="handleSend"
          @typing="handleTyping"
        />
      </div>

      <!-- Online users sidebar (desktop) -->
      <aside class="hidden lg:flex w-56 shrink-0 flex-col border-l border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-900/50">
        <div class="px-3 py-2 border-b border-gray-200 dark:border-gray-800">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            Online <span class="ml-1 text-brand">{{ onlineUsers.length }}</span>
          </h3>
        </div>
        <div class="flex-1 overflow-y-auto py-2">
          <div
            v-for="user in onlineUsers"
            :key="user.name"
            class="flex items-center gap-2 px-3 py-1.5"
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
            <span
              class="text-sm truncate"
              :class="user.name === displayName ? 'font-medium text-brand dark:text-brand-light' : 'text-gray-700 dark:text-gray-300'"
            >
              {{ user.name }}{{ user.name === displayName ? ' (you)' : '' }}
            </span>
          </div>
        </div>
      </aside>
    </div>

    <!-- Online users toggle button (mobile) -->
    <button
      class="lg:hidden fixed bottom-20 right-4 z-40 w-10 h-10 rounded-full bg-brand hover:bg-brand-dark text-white flex items-center justify-center shadow-lg transition-colors cursor-pointer"
      @click="showUsersPanel = !showUsersPanel"
      title="Online users"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <span
        v-if="onlineUsers.length > 0"
        class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-green-500 text-white text-[10px] flex items-center justify-center font-bold"
      >
        {{ onlineUsers.length }}
      </span>
    </button>

    <!-- Online users panel (mobile overlay) -->
    <div
      v-if="showUsersPanel"
      class="lg:hidden fixed inset-0 z-50"
    >
      <div class="absolute inset-0 bg-black/30" @click="showUsersPanel = false"></div>
      <div class="absolute right-0 top-0 bottom-0 w-64 bg-white dark:bg-gray-900 shadow-xl flex flex-col animate-slide-in-right">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white">
            Online <span class="text-brand">{{ onlineUsers.length }}</span>
          </h3>
          <button
            @click="showUsersPanel = false"
            class="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto py-2">
          <div
            v-for="user in onlineUsers"
            :key="user.name"
            class="flex items-center gap-2 px-4 py-2"
          >
            <div
              v-if="user.avatar && getAvatarById(user.avatar)"
              class="w-7 h-7 rounded-full overflow-hidden shrink-0"
              v-html="getAvatarById(user.avatar).svg"
            ></div>
            <span
              v-else
              class="w-7 h-7 rounded-full bg-brand/20 text-brand text-xs font-bold flex items-center justify-center shrink-0"
            >
              {{ user.name.charAt(0).toUpperCase() }}
            </span>
            <span
              class="text-sm truncate"
              :class="user.name === displayName ? 'font-medium text-brand dark:text-brand-light' : 'text-gray-700 dark:text-gray-300'"
            >
              {{ user.name }}{{ user.name === displayName ? ' (you)' : '' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Display name modal -->
    <DisplayNameModal
      v-if="showNameModal"
      @submit="handleNameSubmit"
    />

    <!-- Expired overlay -->
    <RoomExpiredOverlay v-if="isExpired" />
  </div>
</template>
