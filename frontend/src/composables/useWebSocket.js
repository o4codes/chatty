import { ref, onUnmounted } from 'vue'

export function useWebSocket(roomId, { onMessage, onClose, onError } = {}) {
  const isConnected = ref(false)
  let ws = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 3
  let reconnectTimeout = null
  let closed = false

  function buildUrl() {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    return `${protocol}://${location.host}/ws/${roomId}`
  }

  function connect() {
    if (closed) return

    ws = new WebSocket(buildUrl())

    ws.onopen = () => {
      isConnected.value = true
      reconnectAttempts = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage?.(data)
      } catch {
        // Ignore malformed messages
      }
    }

    ws.onclose = (event) => {
      isConnected.value = false

      if (closed) return

      if (event.code === 4001) {
        onClose?.('expired')
        return
      }

      if (event.code === 4004) {
        onClose?.('not_found')
        return
      }

      if (event.code === 1000 || event.code === 1001) {
        onClose?.('normal')
        return
      }

      // Unexpected close — attempt reconnect
      attemptReconnect()
    }

    ws.onerror = () => {
      onError?.()
    }
  }

  function attemptReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
      onClose?.('failed')
      return
    }

    const delay = Math.pow(2, reconnectAttempts) * 1000
    reconnectAttempts++

    reconnectTimeout = setTimeout(() => {
      connect()
    }, delay)
  }

  function send(payload) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        ...payload,
        timestamp: new Date().toISOString(),
      }))
    }
  }

  function close() {
    closed = true
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
    }
    if (ws) {
      ws.close(1000)
      ws = null
    }
    isConnected.value = false
  }

  onUnmounted(close)

  return { connect, send, close, isConnected, reconnecting: ref(false) }
}
