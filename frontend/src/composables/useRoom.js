import { ref } from 'vue'

export function useRoom() {
  const loading = ref(false)
  const error = ref(null)

  async function createRoom() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/rooms/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      })
      if (!res.ok) {
        throw new Error('Failed to create room')
      }
      return await res.json()
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  async function getRoom(roomId) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`/api/rooms/${roomId}`)
      if (res.status === 404) {
        return null
      }
      if (!res.ok) {
        throw new Error('Failed to fetch room')
      }
      return await res.json()
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      loading.value = false
    }
  }

  return { createRoom, getRoom, loading, error }
}
