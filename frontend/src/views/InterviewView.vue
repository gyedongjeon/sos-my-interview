<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useInterviewStore } from '../stores/interview'
import { useSpeech } from '../composables/useSpeech'
import { useCamera } from '../composables/useCamera'
import { useSpeechRecognition } from '../composables/useSpeechRecognition'
import type { Phase, Turn } from '../types'

const MAX_FOLLOW_UPS = 2

const props = defineProps<{ id: number }>()

const store = useInterviewStore()
const question = computed(() => store.byId(props.id))
const speech = useSpeech()
const camera = useCamera()
const recognition = useSpeechRecognition()

const videoEl = ref<HTMLVideoElement | null>(null)
const prompt = ref('') // Question currently being asked (the picked one or a follow-up).
const turns = ref<Turn[]>([]) // Finished answers for the picked question.
const followUps = ref(0)
const phase = ref<Phase>('idle')
const error = ref('')

const isFollowUp = computed(() => followUps.value > 0)
const busy = computed(() => ['recording', 'transcribing', 'thinking'].includes(phase.value))

function resetThread() {
  turns.value.forEach((t) => t.recordingUrl && URL.revokeObjectURL(t.recordingUrl))
  turns.value = []
  followUps.value = 0
  phase.value = 'idle'
  error.value = ''
}

function ask(text: string) {
  prompt.value = text
  speech.speak(text)
}

async function startAnswer() {
  error.value = ''
  speech.stop()
  if (!camera.startRecording()) {
    error.value = 'The microphone is not available, so the answer cannot be recorded.'
    return
  }
  recognition.start()
  phase.value = 'recording'
}

// Transcribes the answer with the local Whisper model on the backend.
async function transcribe(audio: Blob): Promise<string> {
  const form = new FormData()
  form.append('file', audio, 'answer.webm')
  const res = await fetch('/api/transcribe', { method: 'POST', body: form })
  const data = (await res.json()) as { text?: string; detail?: string }
  if (!res.ok) throw new Error(data.detail ?? `HTTP ${res.status}`)
  return data.text ?? ''
}

async function stopAnswer() {
  phase.value = 'transcribing'
  const [recording, liveCaption] = await Promise.all([camera.stopRecording(), recognition.stop()])

  // Whisper is the accurate transcript; the browser's live caption is only a fallback.
  let answer = liveCaption
  if (recording.audio) {
    try {
      answer = await transcribe(recording.audio)
    } catch (e) {
      error.value = `${(e as Error).message}. Using the live caption instead.`
    }
  }
  turns.value.push({ question: prompt.value, answer, recordingUrl: recording.url, hasVideo: camera.hasVideo() })
  phase.value = 'thinking'

  store.markAnswered(props.id)
  if (!answer) {
    error.value = 'No speech was recognized, so there is no follow-up. Try answering again.'
    phase.value = 'idle'
    return
  }
  if (followUps.value >= MAX_FOLLOW_UPS) {
    phase.value = 'done'
    return
  }
  try {
    const res = await fetch('/api/follow-up', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        turns: turns.value.filter((t) => t.answer).map(({ question, answer }) => ({ question, answer })),
      }),
    })
    const data = (await res.json()) as { question?: string; detail?: string }
    if (!res.ok || !data.question) throw new Error(data.detail ?? `HTTP ${res.status}`)
    followUps.value++
    phase.value = 'idle'
    ask(data.question)
  } catch (e) {
    error.value = `Could not get a follow-up question: ${(e as Error).message}`
    phase.value = 'idle'
  }
}

// The picked question starts a fresh thread and is read aloud once it is available.
watch(
  question,
  (q) => {
    resetThread()
    if (q) ask(q.text)
  },
  { immediate: true },
)

watch([videoEl, camera.stream], ([el, stream]) => {
  if (el) el.srcObject = stream
})

onMounted(() => {
  store.load()
  camera.open()
})

onBeforeUnmount(() => {
  speech.stop()
  recognition.stop()
  camera.close()
  resetThread()
})
</script>

<template>
  <main class="mx-auto max-w-5xl p-4 sm:p-8">
    <div v-if="store.loading" class="flex justify-center py-24">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>

    <div v-else-if="store.loaded && !question" role="alert" class="alert alert-warning">
      <span>This question does not exist.</span>
      <RouterLink class="btn btn-sm" to="/">Back to questions</RouterLink>
    </div>

    <template v-else-if="question">
      <div class="mb-4 flex items-center justify-between">
        <RouterLink class="btn btn-ghost btn-sm" to="/">← Questions</RouterLink>
        <span class="badge" :class="isFollowUp ? 'badge-primary' : 'badge-neutral'">
          {{ isFollowUp ? `Follow-up ${followUps} / ${MAX_FOLLOW_UPS}` : 'Main question' }}
        </span>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div
          class="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-box bg-neutral ring-4 transition"
          :class="speech.speaking.value ? 'ring-success' : 'ring-transparent'"
        >
          <svg class="w-2/5" viewBox="0 0 120 120" aria-hidden="true">
            <circle cx="60" cy="60" r="60" fill="#3d4654" />
            <circle cx="60" cy="46" r="20" fill="#c9d1d9" />
            <path d="M22 104c4-22 20-32 38-32s34 10 38 32a60 60 0 0 1-76 0z" fill="#c9d1d9" />
          </svg>
          <span class="badge badge-neutral absolute bottom-3 left-3">Interviewer</span>
        </div>

        <div
          class="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-box bg-neutral ring-4 transition"
          :class="phase === 'recording' ? 'ring-success' : 'ring-transparent'"
        >
          <video ref="videoEl" class="h-full w-full -scale-x-100 object-cover" autoplay muted playsinline></video>
          <p v-if="camera.error.value" class="absolute inset-x-0 p-4 text-center text-neutral-content">
            {{ camera.error.value }}
          </p>
          <span v-if="phase === 'recording'" class="badge badge-error absolute right-3 top-3">● REC</span>
          <span class="badge badge-neutral absolute bottom-3 left-3">You</span>
        </div>
      </div>

      <div class="card mt-4 bg-base-100 shadow-sm">
        <div class="card-body">
          <h2 class="text-2xl font-semibold leading-snug">{{ prompt }}</h2>

          <p v-if="phase === 'recording'" class="min-h-6 text-base-content/70">
            {{ recognition.transcript.value || 'Listening…' }}
          </p>
          <p v-if="phase === 'transcribing'" class="flex items-center gap-2 text-base-content/70">
            <span class="loading loading-dots loading-sm"></span> Transcribing your answer…
          </p>
          <p v-if="phase === 'thinking'" class="flex items-center gap-2 text-base-content/70">
            <span class="loading loading-dots loading-sm"></span> Preparing a follow-up question…
          </p>
          <div v-if="phase === 'done'" role="alert" class="alert alert-success alert-soft">
            <span>That's all for this question.</span>
            <RouterLink class="btn btn-sm" to="/">Pick another question</RouterLink>
          </div>
          <div v-if="error" role="alert" class="alert alert-error alert-soft">{{ error }}</div>

          <div class="card-actions mt-2 justify-end">
              <button
                class="btn"
                :disabled="!speech.supported || busy"
                @click="speech.speaking.value ? speech.stop() : speech.speak(prompt)"
              >
                {{ speech.speaking.value ? 'Stop voice' : 'Replay question' }}
              </button>
              <button v-if="phase === 'recording'" class="btn btn-error" @click="stopAnswer">Stop answer</button>
              <button
                v-else
                class="btn btn-primary"
                :disabled="phase !== 'idle' || !camera.stream.value"
                @click="startAnswer"
              >
                Start answer
              </button>
          </div>
        </div>
      </div>

      <div v-if="turns.length" class="mt-4 grid gap-3">
        <div v-for="(turn, i) in turns" :key="i" class="card bg-base-100 shadow-sm">
          <div class="card-body gap-2">
            <p class="font-semibold">{{ turn.question }}</p>
            <p class="text-base-content/70">{{ turn.answer || '(no speech recognized)' }}</p>
            <div v-if="turn.recordingUrl && turn.hasVideo" class="collapse collapse-arrow bg-base-200">
              <input type="checkbox" />
              <div class="collapse-title text-sm">Watch recording</div>
              <div class="collapse-content">
                <video class="w-full max-w-lg rounded-box" :src="turn.recordingUrl" controls playsinline></video>
                <a
                  class="btn btn-sm mt-2"
                  :href="turn.recordingUrl"
                  :download="`answer-q${id}-${i + 1}.webm`"
                >
                  Download
                </a>
              </div>
            </div>
            <div v-else-if="turn.recordingUrl" class="flex flex-wrap items-center gap-2">
              <audio class="h-10 grow" :src="turn.recordingUrl" controls></audio>
              <a class="btn btn-sm" :href="turn.recordingUrl" :download="`answer-q${id}-${i + 1}.webm`">
                Download
              </a>
            </div>
          </div>
        </div>
      </div>
    </template>
  </main>
</template>
