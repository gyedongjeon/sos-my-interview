<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import FeedbackPanel from '../components/FeedbackPanel.vue'
import TurnList from '../components/TurnList.vue'
import { useSpeech } from '../composables/useSpeech'
import { formatDay, formatTime } from '../dates'
import { mean } from '../scores'
import type { AttemptDetail, Turn } from '../types'

const props = defineProps<{ id: number }>()

const router = useRouter()
const speech = useSpeech()
const attempt = ref<AttemptDetail | null>(null)
const error = ref('')
const deleting = ref(false)

const turns = computed<Turn[]>(() =>
  (attempt.value?.turns ?? []).map((t) => ({
    question: t.question,
    answer: t.answer,
    delivery:
      t.clarity === null
        ? null
        : { clarity: t.clarity, unclearWords: t.unclear_words, wordsPerMinute: t.words_per_minute },
    recordingUrl: t.recording_url,
    hasVideo: t.has_video,
  })),
)
const clarity = computed(() => {
  const scores = turns.value.flatMap((t) => (t.delivery ? [t.delivery.clarity] : []))
  return scores.length ? mean(scores) : null
})

async function remove() {
  if (!window.confirm('Delete this attempt and its recordings? This cannot be undone.')) return
  deleting.value = true
  try {
    await api(`/attempts/${props.id}`, { method: 'DELETE' })
    router.push({ name: 'history' })
  } catch (e) {
    error.value = `Could not delete: ${(e as Error).message}`
    deleting.value = false
  }
}

onMounted(async () => {
  try {
    attempt.value = await api<AttemptDetail>(`/attempts/${props.id}`)
  } catch (e) {
    error.value = `Could not load this attempt: ${(e as Error).message}`
  }
})

onBeforeUnmount(speech.stop)
</script>

<template>
  <main class="mx-auto max-w-5xl p-4 sm:p-8">
    <div class="mb-4 flex items-center justify-between">
      <RouterLink class="btn btn-ghost btn-sm" to="/history">← History</RouterLink>
      <div v-if="attempt" class="flex gap-2">
        <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'interview', params: { id: attempt.question_id } }">
          Retry this question
        </RouterLink>
        <button class="btn btn-error btn-outline btn-sm" :disabled="deleting" @click="remove">Delete</button>
      </div>
    </div>

    <div v-if="error" role="alert" class="alert alert-error">{{ error }}</div>
    <div v-else-if="!attempt" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <template v-else>
      <header class="mb-4">
        <p class="text-sm text-base-content/60">
          {{ attempt.posting_title ?? 'Common questions' }} · {{ formatDay(attempt.created_at) }} ·
          {{ formatTime(attempt.created_at) }}
        </p>
        <h1 class="text-2xl font-semibold">{{ attempt.question }}</h1>
      </header>

      <FeedbackPanel
        v-if="attempt.feedback"
        :feedback="attempt.feedback"
        :speaking="attempt.speaking"
        :clarity="clarity"
        @listen="speech.speak"
      />
      <div v-else role="alert" class="alert alert-soft">This attempt was not scored.</div>

      <TurnList class="mt-4" :turns="turns" :download-prefix="`attempt-${attempt.id}`" />
    </template>
  </main>
</template>
