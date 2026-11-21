import { ref } from 'vue'

// Live speech-to-text via the browser Web Speech API (Chrome, Edge, Safari).
export function useSpeechRecognition(lang = 'en-US') {
  const Recognition = window.SpeechRecognition ?? window.webkitSpeechRecognition
  const supported = Boolean(Recognition)
  const transcript = ref('')

  let rec: SpeechRecognition | null = null
  let active = false
  let finalText = ''
  let onStopped: (() => void) | null = null

  function start() {
    if (!Recognition) return
    finalText = ''
    transcript.value = ''
    active = true
    const r = new Recognition()
    rec = r
    r.lang = lang
    r.continuous = true
    r.interimResults = true
    r.onresult = (e) => {
      let interim = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const text = e.results[i][0].transcript
        if (e.results[i].isFinal) finalText += text.trim() + ' '
        else interim += text
      }
      transcript.value = (finalText + interim).trim()
    }
    r.onend = () => {
      // The browser ends recognition after a pause; keep going until stop() is called.
      if (active) {
        try {
          r.start()
          return
        } catch {
          active = false
        }
      }
      onStopped?.()
    }
    r.start()
  }

  // Resolves with the final transcript once the recognizer has flushed its results.
  function stop(): Promise<string> {
    return new Promise((resolve) => {
      if (!rec || !active) return resolve(transcript.value)
      active = false
      const finish = () => {
        onStopped = null
        transcript.value = finalText.trim() || transcript.value
        resolve(transcript.value)
      }
      onStopped = finish
      setTimeout(() => onStopped && finish(), 2000)
      rec.stop()
    })
  }

  return { supported, transcript, start, stop }
}
