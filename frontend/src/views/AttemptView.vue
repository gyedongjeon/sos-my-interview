<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import FeedbackPanel from '../components/FeedbackPanel.vue'
import TurnList from '../components/TurnList.vue'
import { useSpeech } from '../composables/useSpeech'
import { formatDay, formatTime } from '../dates'
import { t } from '../i18n'
import { mean } from '../scores'
import type { AttemptDetail, Turn } from '../types'
import MorseSignal from '../components/MorseSignal.vue'

const props = defineProps<{ id: number }>()

const router = useRouter()
const speech = useSpeech()
const attempt = ref<AttemptDetail | null>(null)
const error = ref('')
const deleting = ref(false)

const turns = computed<Turn[]>(() =>
  (attempt.value?.turns ?? []).map((turn) => ({
    question: turn.question,
    answer: turn.answer,
    delivery:
      turn.clarity === null
        ? null
        : { clarity: turn.clarity, unclearWords: turn.unclear_words, wordsPerMinute: turn.words_per_minute },
    recordingUrl: turn.recording_url,
    hasVideo: turn.has_video,
  })),
)
const clarity = computed(() => {
  const scores = turns.value.flatMap((turn) => (turn.delivery ? [turn.delivery.clarity] : []))
  return scores.length ? mean(scores) : null
})

async function remove() {
  if (!window.confirm(t('attempt.confirmDelete'))) return
  deleting.value = true
  try {
    await api(`/attempts/${props.id}`, { method: 'DELETE' })
    router.push({ name: 'history' })
  } catch (e) {
    error.value = t('attempt.deleteFailed', { error: (e as Error).message })
    deleting.value = false
  }
}

onMounted(async () => {
  try {
    attempt.value = await api<AttemptDetail>(`/attempts/${props.id}`)
  } catch (e) {
    error.value = t('attempt.loadFailed', { error: (e as Error).message })
  }
})

onBeforeUnmount(speech.stop)
</script>

<template>
  <main class="mx-auto max-w-5xl p-4 sm:p-8">
    <div class="mb-4 flex items-center justify-between">
      <RouterLink class="btn btn-ghost btn-sm" to="/history">{{ t('history.back') }}</RouterLink>
      <div v-if="attempt" class="flex gap-2">
        <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'interview', params: { id: attempt.question_id } }">
          {{ t('attempt.retry') }}
        </RouterLink>
        <button class="btn btn-error btn-outline btn-sm" :disabled="deleting" @click="remove">{{ t('common.delete') }}</button>
      </div>
    </div>

    <div v-if="error" role="alert" class="alert alert-error">{{ error }}</div>
    <div v-else-if="!attempt" class="flex justify-center py-16">
      <MorseSignal animated />
    </div>

    <template v-else>
      <header class="mb-4">
        <p class="text-sm text-base-content/60">
          {{ attempt.posting_title ?? t('common.commonQuestions') }} · {{ formatDay(attempt.created_at) }} ·
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
      <div v-else role="alert" class="alert alert-soft">{{ t('attempt.notScored') }}</div>

      <TurnList class="mt-4" :turns="turns" :download-prefix="`attempt-${attempt.id}`" />
    </template>
  </main>
</template>
