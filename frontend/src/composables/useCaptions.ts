import { useSpeechRecognition } from './useSpeechRecognition'
import { useWhisperCaptions } from './useWhisperCaptions'

// Live captions while answering. Browsers caption with the Web Speech API; the desktop app
// (Electron), where that API has no speech service behind it, uses the local Whisper model.
export function useCaptions() {
  const browser = useSpeechRecognition()
  if (browser.supported && !navigator.userAgent.includes('Electron')) {
    return {
      transcript: browser.transcript,
      start: (_stream: MediaStream | null) => browser.start(),
      stop: browser.stop,
    }
  }
  return useWhisperCaptions()
}
