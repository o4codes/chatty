import { ref } from 'vue'

export function useNotificationSound() {
  const enabled = ref(true)
  let audioContext = null

  function getContext() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
    }
    return audioContext
  }

  function play() {
    if (!enabled.value) return

    try {
      const ctx = getContext()

      if (ctx.state === 'suspended') {
        ctx.resume()
      }

      const oscillator = ctx.createOscillator()
      const gainNode = ctx.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(ctx.destination)

      oscillator.frequency.setValueAtTime(830, ctx.currentTime)
      oscillator.frequency.setValueAtTime(1046, ctx.currentTime + 0.1)
      oscillator.type = 'sine'

      gainNode.gain.setValueAtTime(0, ctx.currentTime)
      gainNode.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.02)
      gainNode.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1)
      gainNode.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.25)

      oscillator.start(ctx.currentTime)
      oscillator.stop(ctx.currentTime + 0.25)
    } catch {
      // Silently fail — sound is not critical
    }
  }

  return { play, enabled }
}
