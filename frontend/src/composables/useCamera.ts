import { ref, shallowRef } from 'vue'

/** Why a device could not be opened, in words the user can act on. */
export function deviceProblem(device: 'microphone' | 'camera', failure: unknown): string {
  const name = failure instanceof Error ? failure.name : ''
  if (name === 'NotFoundError') return `No ${device} was found.`
  if (name === 'NotAllowedError') {
    const Device = device[0].toUpperCase() + device.slice(1)
    return `${Device} access is turned off. Allow it for this app in your system's privacy settings.`
  }
  if (name === 'NotReadableError') return `The ${device} could not be started. Close other apps that use it.`
  return name ? `The ${device} is not available (${name}).` : `The ${device} is not available.`
}

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
    let cameraFailure: unknown
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      return
    } catch (e) {
      // Fall through: the answer only needs the microphone, so retry without the camera.
      cameraFailure = e
    }
    try {
      stream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
      error.value = `${deviceProblem('camera', cameraFailure)} Only your voice is recorded.`
    } catch (e) {
      error.value = `${deviceProblem('microphone', e)} Answers cannot be recorded until this is fixed; then open this page again.`
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
    // Low bitrates keep saved recordings small (roughly 2 MB per minute).
    recorder = new MediaRecorder(stream.value, { videoBitsPerSecond: 250_000, audioBitsPerSecond: 48_000 })
    recorder.ondataavailable = (e) => {
      if (e.data.size) chunks.push(e.data)
    }
    audioRecorder = new MediaRecorder(new MediaStream(audioTracks), { audioBitsPerSecond: 48_000 })
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

  // Resolves with the full recording (to replay and save) and the audio-only one (to analyze).
  async function stopRecording(): Promise<{ recording: Blob | null; audio: Blob | null }> {
    const [recording, audio] = await Promise.all([
      finish(recorder, () => chunks),
      finish(audioRecorder, () => audioChunks),
    ])
    return { recording, audio }
  }

  // False when only the microphone could be opened, so recordings have no picture.
  const hasVideo = () => Boolean(stream.value?.getVideoTracks().length)

  return { stream, error, hasVideo, open, close, startRecording, stopRecording }
}
