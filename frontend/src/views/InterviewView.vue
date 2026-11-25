<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { api } from '../api'
import FeedbackPanel from '../components/FeedbackPanel.vue'
import TurnList from '../components/TurnList.vue'
import { useCamera } from '../composables/useCamera'
import { useSpeech } from '../composables/useSpeech'
import { useCaptions } from '../composables/useCaptions'
import { t } from '../i18n'
import { contentScores, englishScores, mean, total } from '../scores'
import { useInterviewStore } from '../stores/interview'
import { percent, useModelsStore } from '../stores/models'
import type { AttemptSummary, Delivery, Feedback, LiveTurn, Phase, SpeakingFeedback } from '../types'
import MorseSignal from '../components/MorseSignal.vue'

const MAX_FOLLOW_UPS = 2

const props = defineProps<{ id: number }>()

const store = useInterviewStore()
const question = computed(() => store.byId(props.id))
const speech = useSpeech()
const camera = useCamera()
const recognition = useCaptions()

const videoEl = ref<HTMLVideoElement | null>(null)
const prompt = ref('') // Question currently being asked (the picked one or a follow-up).
// The question is heard first, as in a real interview; its text is shown only on request.
const showPrompt = ref(false)
const turns = ref<LiveTurn[]>([]) // Finished answers of the attempt in progress.
const followUps = ref(0)
const phase = ref<Phase>('idle')
const error = ref('')
const notice = ref('') // Non-blocking problems, e.g. a part of the feedback that is missing.
const feedback = ref<Feedback | null>(null)
const speaking = ref<SpeakingFeedback | null>(null)
const feedbackLoading = ref(false)
// The saved attempt these answers belong to; created with the first answer.
const attemptId = ref<number | null>(null)
// The latest scored attempt at this question before the current one, for comparison.
const previous = ref<AttemptSummary | null>(null)

const isFollowUp = computed(() => followUps.value > 0)
// Set while the speech recognition model is still downloading, which the first answer waits for.
const models = useModelsStore()
const recognitionDownload = computed(() => {
  const model = models.byId('speech-to-text')
  return model?.state === 'downloading' ? model : null
})
watch(phase, (now) => {
  if (now === 'transcribing') void models.check()
})
// The list this question was picked from: its job posting's page or the common questions.
const backTo = computed(() => {
  const postingId = question.value?.posting_id
  return postingId ? { name: 'posting', params: { id: postingId } } : { name: 'common' }
})
const busy = computed(() => ['recording', 'transcribing', 'thinking'].includes(phase.value))
const answered = computed(() => turns.value.filter((t) => t.answer))
const clarity = computed(() => {
  const scores = turns.value.flatMap((t) => (t.delivery ? [t.delivery.clarity] : []))
  return scores.length ? mean(scores) : null
})

function resetThread() {
  turns.value.forEach((t) => t.recordingUrl && URL.revokeObjectURL(t.recordingUrl))
  turns.value = []
  followUps.value = 0
  phase.value = 'idle'
  error.value = ''
  notice.value = ''
  feedback.value = null
  speaking.value = null
  attemptId.value = null
}

function ask(text: string) {
  prompt.value = text
  showPrompt.value = false
  speech.speak(text)
}

async function loadPrevious() {
  await store.loadAttempts()
  previous.value =
    store.attemptsFor(props.id).find((a) => a.id !== attemptId.value && a.english_score !== null) ?? null
}

// Starts a new attempt at the same question, to compare against the one just scored.
async function retry() {
  const q = question.value
  if (!q) return
  resetThread()
  await loadPrevious()
  ask(q.text)
}

function startAnswer() {
  error.value = ''
  notice.value = ''
  // Feedback covers the whole attempt, so a new answer makes it stale.
  feedback.value = null
  speaking.value = null
  speech.stop()
  if (!camera.startRecording()) {
    error.value = t('interview.micUnavailable')
    return
  }
  // Captions are optional; the answer is still recorded and transcribed without them.
  void Promise.resolve(recognition.start(camera.stream.value)).catch(() => {})
  phase.value = 'recording'
}

// Transcribes the answer with the local Whisper model on the backend.
async function transcribe(audio: Blob): Promise<{ text: string; delivery: Delivery | null }> {
  const form = new FormData()
  form.append('file', audio, 'answer.webm')
  const data = await api<{
    text: string
    clarity: number | null
    unclear_words: string[]
    words_per_minute: number | null
  }>('/transcribe', { method: 'POST', body: form })
  const delivery =
    data.clarity === null
      ? null
      : { clarity: data.clarity, unclearWords: data.unclear_words, wordsPerMinute: data.words_per_minute }
  return { text: data.text, delivery }
}

// Saves the answer and its recording so it shows up in History.
async function saveTurn(turn: LiveTurn, recording: Blob | null) {
  attemptId.value ??= (await api<AttemptSummary>('/attempts', { method: 'POST', json: { question_id: props.id } })).id
  const form = new FormData()
  form.append('question', turn.question)
  form.append('answer', turn.answer)
  form.append('has_video', String(turn.hasVideo))
  if (turn.delivery) {
    form.append('clarity', String(turn.delivery.clarity))
    form.append('unclear_words', JSON.stringify(turn.delivery.unclearWords))
    if (turn.delivery.wordsPerMinute !== null) form.append('words_per_minute', String(turn.delivery.wordsPerMinute))
  }
  if (recording) form.append('recording', recording, 'recording.webm')
  await api(`/attempts/${attemptId.value}/turns`, { method: 'POST', body: form })
}

async function stopAnswer() {
  phase.value = 'transcribing'
  const [{ recording, audio }, liveCaption] = await Promise.all([camera.stopRecording(), recognition.stop()])

  // Whisper is the accurate transcript; the browser's live caption is only a fallback.
  let answer = liveCaption
  let delivery: Delivery | null = null
  if (audio) {
    try {
      ;({ text: answer, delivery } = await transcribe(audio))
    } catch (e) {
      notice.value = t('interview.usingCaption', { error: (e as Error).message })
    }
  }
  const turn: LiveTurn = {
    question: prompt.value,
    answer,
    delivery,
    audio,
    recordingUrl: recording ? URL.createObjectURL(recording) : null,
    hasVideo: camera.hasVideo(),
  }
  turns.value.push(turn)
  try {
    await saveTurn(turn, recording)
  } catch (e) {
    notice.value = t('interview.notSaved', { error: (e as Error).message })
  }

  if (!answer) {
    error.value = t('interview.noSpeech')
    phase.value = 'idle'
    return
  }
  if (followUps.value >= MAX_FOLLOW_UPS) {
    phase.value = 'done'
    requestFeedback()
    return
  }
  phase.value = 'thinking'
  try {
    const data = await api<{ question: string }>('/follow-up', {
      method: 'POST',
      json: {
        question_id: props.id,
        turns: answered.value.map(({ question, answer }) => ({ question, answer })),
      },
    })
    followUps.value++
    phase.value = 'idle'
    ask(data.question)
  } catch (e) {
    error.value = t('interview.followUpFailed', { error: (e as Error).message })
    phase.value = 'idle'
  }
}

// Scores how the answers sound, by sending the audio to a model that can listen.
function evaluateSpeaking(): Promise<SpeakingFeedback> {
  const form = new FormData()
  for (const turn of answered.value) {
    if (!turn.audio) continue
    form.append('files', turn.audio, 'answer.webm')
    form.append('questions', turn.question)
    form.append('transcripts', turn.answer)
  }
  return api<SpeakingFeedback>('/evaluate/speaking', { method: 'POST', body: form })
}

async function requestFeedback() {
  error.value = ''
  notice.value = ''
  feedbackLoading.value = true
  try {
    const hasAudio = answered.value.some((t) => t.audio)
    const [text, spoken] = await Promise.allSettled([
      api<Feedback>('/evaluate', {
        method: 'POST',
        json: {
          question_id: props.id,
          turns: answered.value.map(({ question, answer }) => ({ question, answer })),
        },
      }),
      hasAudio ? evaluateSpeaking() : Promise.reject(new Error(t('interview.noAudio'))),
    ])
    if (text.status === 'rejected') throw text.reason
    feedback.value = text.value
    if (spoken.status === 'fulfilled') {
      speaking.value = spoken.value
    } else {
      // Not every model accepts audio; the sentence and content scores still stand.
      notice.value = t('interview.speakingNotScored', { error: (spoken.reason as Error).message })
    }
    if (attemptId.value !== null) {
      await api(`/attempts/${attemptId.value}/feedback`, {
        method: 'PUT',
        json: {
          feedback: feedback.value,
          speaking: speaking.value,
          english_score: total(englishScores(feedback.value, speaking.value, clarity.value)),
          content_score: total(contentScores(feedback.value)),
        },
      })
    }
  } catch (e) {
    error.value = t('interview.feedbackFailed', { error: (e as Error).message })
  } finally {
    feedbackLoading.value = false
  }
}

// The picked question starts a fresh attempt and is read aloud once it is available.
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
  store.load(true)
  loadPrevious()
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
      <MorseSignal animated />
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>

    <div v-else-if="store.loaded && !question" role="alert" class="alert alert-warning">
      <span>{{ t('interview.notFound') }}</span>
      <RouterLink class="btn btn-sm" to="/">{{ t('interview.backToQuestions') }}</RouterLink>
    </div>

    <template v-else-if="question">
      <div class="mb-4 flex items-center justify-between">
        <RouterLink class="btn btn-ghost btn-sm" :to="backTo">{{ t('interview.back') }}</RouterLink>
        <span class="badge" :class="isFollowUp ? 'badge-primary' : 'badge-neutral'">
          {{ isFollowUp ? t('interview.followUp', { n: followUps, total: MAX_FOLLOW_UPS }) : t('interview.main') }}
        </span>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div
          class="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-box bg-neutral ring-4 transition"
          :class="speech.speaking.value ? 'ring-primary' : 'ring-transparent'"
        >
          <svg class="w-2/5" viewBox="0 0 120 120" aria-hidden="true">
            <circle cx="60" cy="60" r="60" class="fill-neutral-content/10" />
            <circle cx="60" cy="46" r="20" class="fill-neutral-content/70" />
            <path d="M22 104c4-22 20-32 38-32s34 10 38 32a60 60 0 0 1-76 0z" class="fill-neutral-content/70" />
          </svg>
          <span class="badge badge-neutral absolute bottom-3 left-3">{{ t('interview.interviewer') }}</span>
        </div>

        <div
          class="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-box bg-neutral ring-4 transition"
          :class="phase === 'recording' ? 'ring-primary' : 'ring-transparent'"
        >
          <video ref="videoEl" class="h-full w-full -scale-x-100 object-cover" autoplay muted playsinline></video>
          <p v-if="camera.error.value" class="absolute inset-x-0 p-4 text-center text-neutral-content">
            {{ camera.error.value }}
          </p>
          <span v-if="phase === 'recording'" class="badge badge-error absolute right-3 top-3 font-semibold">
            <span class="size-2 animate-pulse rounded-full bg-current"></span> REC
          </span>
          <span class="badge badge-neutral absolute bottom-3 left-3">{{ t('interview.you') }}</span>
        </div>
      </div>

      <div class="card mt-4 bg-base-100 shadow-sm">
        <div class="card-body">
          <div class="flex items-start justify-between gap-3">
            <h2 v-if="showPrompt" class="text-2xl font-semibold leading-snug">{{ prompt }}</h2>
            <p v-else class="text-lg text-base-content/60">{{ t('interview.listenFirst') }}</p>
            <button class="btn btn-sm shrink-0" :aria-expanded="showPrompt" @click="showPrompt = !showPrompt">
              {{ showPrompt ? t('interview.hide') : t('interview.show') }}
            </button>
          </div>

          <p v-if="phase === 'recording'" class="min-h-6 text-base-content/70">
            {{ recognition.transcript.value || t('interview.listening') }}
          </p>
          <p v-if="phase === 'transcribing'" class="flex items-center gap-2 text-base-content/70">
            <span class="loading loading-dots loading-sm"></span>
            <template v-if="recognitionDownload">
              {{
                t('interview.downloadingRecognition', {
                  percent: percent(recognitionDownload) === null ? '' : ` — ${percent(recognitionDownload)}%`,
                })
              }}
            </template>
            <template v-else>{{ t('interview.transcribing') }}</template>
          </p>
          <p v-if="phase === 'thinking'" class="flex items-center gap-2 text-base-content/70">
            <span class="loading loading-dots loading-sm"></span> {{ t('interview.preparing') }}
          </p>
          <div v-if="phase === 'done'" role="alert" class="alert alert-success alert-soft">
            <span>{{ t('interview.done') }}</span>
            <RouterLink class="btn btn-sm" :to="backTo">{{ t('interview.pickAnother') }}</RouterLink>
          </div>
          <div v-if="notice" role="alert" class="alert alert-warning alert-soft">{{ notice }}</div>
          <div v-if="error" role="alert" class="alert alert-error alert-soft">{{ error }}</div>

          <div class="card-actions mt-2 justify-end">
            <button class="btn" :disabled="busy" @click="speech.speaking.value ? speech.stop() : speech.speak(prompt)">
              {{ speech.speaking.value ? t('interview.stopVoice') : t('interview.replay') }}
            </button>
            <button
              v-if="answered.length && !feedback"
              class="btn"
              :disabled="busy || feedbackLoading"
              @click="requestFeedback"
            >
              <span v-if="feedbackLoading" class="loading loading-spinner loading-xs"></span>
              {{ feedbackLoading ? t('interview.scoring') : t('interview.getFeedback') }}
            </button>
            <button v-if="feedback" class="btn" :disabled="busy" @click="retry">{{ t('common.tryAgain') }}</button>
            <button v-if="phase === 'recording'" class="btn btn-error" @click="stopAnswer">{{ t('interview.stopAnswer') }}</button>
            <button
              v-else
              class="btn btn-primary"
              :disabled="phase !== 'idle' || !camera.stream.value"
              @click="startAnswer"
            >
              {{ t('interview.startAnswer') }}
            </button>
          </div>
        </div>
      </div>

      <FeedbackPanel
        v-if="feedback"
        class="mt-4"
        :feedback="feedback"
        :speaking="speaking"
        :clarity="clarity"
        :previous-english="previous?.english_score"
        :previous-content="previous?.content_score"
        @listen="speech.speak"
      />

      <TurnList v-if="turns.length" class="mt-4" :turns="turns" :download-prefix="`answer-q${id}`" />
    </template>
  </main>
</template>
