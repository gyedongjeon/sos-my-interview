import { ref, shallowRef } from 'vue'

// Webcam + microphone access and answer recording via getUserMedia / MediaRecorder.
export function useCamera() {
  const stream = shallowRef<MediaStream | null>(null)
  const error = ref('')
  let recorder: MediaRecorder | null = null
  let chunks: Blob[] = []
  // A second, audio-only recording: a small upload for transcription.
  let audioRecorder: MediaRecorder | null = null
  let audioChunks: Blob[] = []

  async function open() {
    error.value = ''
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      return
    } catch {
      // Fall through: the answer only needs the microphone, so retry without the camera.
    }
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
      error.value = 'The camera is unavailable, so only your voice is recorded.'
    } catch (e) {
      const err = e as DOMException
      error.value =
        err.name === 'NotAllowedError'
          ? 'Microphone permission was denied. Allow it in the browser and reload.'
          : `Could not open the microphone: ${err.message}`
    }
  }

  function close() {
    if (recorder && recorder.state !== 'inactive') recorder.stop()
    if (audioRecorder && audioRecorder.state !== 'inactive') audioRecorder.stop()
    stream.value?.getTracks().forEach((t) => t.stop())
    stream.value = null
  }

  function startRecording(): boolean {
    const audioTracks = stream.value?.getAudioTracks() ?? []
    if (!stream.value || !audioTracks.length) return false
    chunks = []
    audioChunks = []
    recorder = new MediaRecorder(stream.value)
    recorder.ondataavailable = (e) => {
      if (e.data.size) chunks.push(e.data)
    }
    audioRecorder = new MediaRecorder(new MediaStream(audioTracks))
    audioRecorder.ondataavailable = (e) => {
      if (e.data.size) audioChunks.push(e.data)
    }
    recorder.start()
    audioRecorder.start()
    return true
  }

  function finish(rec: MediaRecorder | null, parts: () => Blob[]): Promise<Blob | null> {
    return new Promise((resolve) => {
      if (!rec || rec.state === 'inactive') return resolve(null)
      rec.onstop = () => {
        const blob = new Blob(parts(), { type: rec.mimeType })
        resolve(blob.size ? blob : null)
      }
      rec.stop()
    })
  }

  // Resolves with a playable URL for the recording and the audio-only blob to transcribe.
  async function stopRecording(): Promise<{ url: string | null; audio: Blob | null }> {
    const [full, audio] = await Promise.all([
      finish(recorder, () => chunks),
      finish(audioRecorder, () => audioChunks),
    ])
    return { url: full ? URL.createObjectURL(full) : null, audio }
  }

  // False when only the microphone could be opened, so recordings have no picture.
  const hasVideo = () => Boolean(stream.value?.getVideoTracks().length)

  return { stream, error, hasVideo, open, close, startRecording, stopRecording }
}
