import { ref } from 'vue'

const SAMPLE_RATE = 16_000
// A chunk is sent at the first pause after MIN_SECONDS, or at MAX_SECONDS without one.
const MIN_SECONDS = 2
const MAX_SECONDS = 8
const PAUSE_SECONDS = 0.4
// Frames quieter than this (RMS, full scale = 1) count as silence.
const SILENCE_RMS = 0.01

// Runs on the audio thread and hands the microphone samples to the page.
const TAP_PROCESSOR = `registerProcessor('pcm-tap', class extends AudioWorkletProcessor {
  process(inputs) {
    const channel = inputs[0][0]
    if (channel) this.port.postMessage(channel.slice())
    return true
  }
})`

function encodeWav(frames: Float32Array[], length: number): Blob {
  const view = new DataView(new ArrayBuffer(44 + length * 2))
  const text = (offset: number, value: string) =>
    [...value].forEach((c, i) => view.setUint8(offset + i, c.charCodeAt(0)))
  text(0, 'RIFF')
  view.setUint32(4, 36 + length * 2, true)
  text(8, 'WAVEfmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, 1, true) // mono
  view.setUint32(24, SAMPLE_RATE, true)
  view.setUint32(28, SAMPLE_RATE * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  text(36, 'data')
  view.setUint32(40, length * 2, true)
  let offset = 44
  for (const frame of frames) {
    for (const sample of frame) {
      view.setInt16(offset, Math.max(-1, Math.min(1, sample)) * 0x7fff, true)
      offset += 2
    }
  }
  return new Blob([view], { type: 'audio/wav' })
}

// Live captions from the local Whisper model: the microphone audio is cut at pauses and each
// piece is transcribed by the backend. Used where the Web Speech API is unavailable.
export function useWhisperCaptions() {
  const transcript = ref('')

  let context: AudioContext | null = null
  let frames: Float32Array[] = []
  let samples = 0
  let silentSamples = 0
  let heardSpeech = false
  // Requests run one after another so the captions stay in order.
  let queue: Promise<void> = Promise.resolve()
  let session = 0

  function flush() {
    const [chunk, length, spoken] = [frames, samples, heardSpeech]
    frames = []
    samples = 0
    silentSamples = 0
    heardSpeech = false
    if (!spoken) return
    const current = session
    queue = queue.then(async () => {
      if (current !== session) return
      const form = new FormData()
      form.append('file', encodeWav(chunk, length), 'chunk.wav')
      try {
        const res = await fetch('/api/captions', { method: 'POST', body: form })
        if (!res.ok || current !== session) return
        const { text } = (await res.json()) as { text: string }
        if (text) transcript.value = `${transcript.value} ${text}`.trim()
      } catch {
        // Captions are best effort; the full recording is transcribed afterwards anyway.
      }
    })
  }

  function onFrame(frame: Float32Array) {
    let sum = 0
    for (const sample of frame) sum += sample * sample
    if (Math.sqrt(sum / frame.length) < SILENCE_RMS) silentSamples += frame.length
    else {
      silentSamples = 0
      heardSpeech = true
    }
    frames.push(frame)
    samples += frame.length
    const paused = silentSamples >= PAUSE_SECONDS * SAMPLE_RATE
    if ((samples >= MIN_SECONDS * SAMPLE_RATE && paused) || samples >= MAX_SECONDS * SAMPLE_RATE) flush()
  }

  async function start(stream: MediaStream | null) {
    await close()
    transcript.value = ''
    const tracks = stream?.getAudioTracks() ?? []
    if (!tracks.length) return
    const current = ++session
    // The context resamples the microphone to the rate Whisper expects.
    const ctx = new AudioContext({ sampleRate: SAMPLE_RATE })
    context = ctx
    const module = URL.createObjectURL(new Blob([TAP_PROCESSOR], { type: 'text/javascript' }))
    try {
      await ctx.audioWorklet.addModule(module)
    } finally {
      URL.revokeObjectURL(module)
    }
    if (current !== session) return
    const tap = new AudioWorkletNode(ctx, 'pcm-tap')
    tap.port.onmessage = (e: MessageEvent<Float32Array>) => {
      if (current === session) onFrame(e.data)
    }
    ctx.createMediaStreamSource(new MediaStream(tracks)).connect(tap)
  }

  async function close() {
    const ctx = context
    context = null
    frames = []
    samples = 0
    if (ctx && ctx.state !== 'closed') await ctx.close()
  }

  // Resolves with the captions so far, waiting briefly for the piece being transcribed.
  async function stop(): Promise<string> {
    if (!context) return transcript.value
    flush()
    await close()
    await Promise.race([queue, new Promise((resolve) => setTimeout(resolve, 2000))])
    session++
    return transcript.value
  }

  return { transcript, start, stop }
}
