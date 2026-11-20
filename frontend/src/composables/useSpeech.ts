import { ref } from 'vue'

// Thin wrapper over the browser Web Speech API (no server or API key needed).
export function useSpeech(lang = 'en-US') {
  const supported = 'speechSynthesis' in window
  const speaking = ref(false)

  function speak(text: string) {
    if (!supported || !text) return
    window.speechSynthesis.cancel()
    const utter = new SpeechSynthesisUtterance(text)
    utter.lang = lang
    utter.rate = 0.95
    utter.onstart = () => (speaking.value = true)
    utter.onend = utter.onerror = () => (speaking.value = false)
    window.speechSynthesis.speak(utter)
  }

  function stop() {
    if (supported) window.speechSynthesis.cancel()
    speaking.value = false
  }

  return { supported, speaking, speak, stop }
}
