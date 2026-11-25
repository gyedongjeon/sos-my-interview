<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { dayKey, formatDay, formatTime } from '../dates'
import { t, type MessageKey } from '../i18n'
import { useInterviewStore } from '../stores/interview'
import type { AttemptSummary } from '../types'
import MorseSignal from '../components/MorseSignal.vue'

const store = useInterviewStore()
const loading = ref(true)

onMounted(async () => {
  await store.loadAttempts()
  loading.value = false
})

// Attempts grouped by local calendar day, newest day first (the list is already newest first).
const days = computed(() => {
  const groups = new Map<string, AttemptSummary[]>()
  for (const attempt of store.attempts) {
    const key = dayKey(attempt.created_at)
    groups.set(key, [...(groups.get(key) ?? []), attempt])
  }
  return [...groups.values()]
})

type ScoreKey = 'english_score' | 'content_score'

// Change in a score against the previous scored attempt at the same question.
function change(attempt: AttemptSummary, key: ScoreKey): number | null {
  const score = attempt[key]
  if (score === null) return null
  const earlier = store.attempts.find(
    (a) => a.question_id === attempt.question_id && a.id < attempt.id && a[key] !== null,
  )
  return earlier ? score - (earlier[key] as number) : null
}

const scores: { key: ScoreKey; label: MessageKey }[] = [
  { key: 'english_score', label: 'score.english' },
  { key: 'content_score', label: 'score.content' },
]
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <h1 class="mb-4 text-2xl font-bold">{{ t('nav.history') }}</h1>

    <div v-if="loading" class="flex justify-center py-16">
      <MorseSignal animated />
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>
    <div v-else-if="!days.length" class="card bg-base-100 shadow-sm">
      <div class="card-body items-center text-center">
        <p>{{ t('history.none') }}</p>
        <RouterLink class="btn btn-primary btn-sm" to="/">{{ t('history.pick') }}</RouterLink>
      </div>
    </div>

    <section v-for="day in days" v-else :key="day[0].id" class="mb-6">
      <h2 class="mb-2 text-sm font-semibold text-base-content/70">{{ formatDay(day[0].created_at) }}</h2>
      <ul class="list rounded-box bg-base-100 shadow-sm">
        <li v-for="attempt in day" :key="attempt.id" class="list-row items-center">
          <div class="w-14 text-sm tabular-nums opacity-60">{{ formatTime(attempt.created_at) }}</div>
          <div class="list-col-grow">
            <p class="text-xs text-base-content/60">{{ attempt.posting_title ?? t('common.commonQuestions') }}</p>
            <p class="font-medium">{{ attempt.question }}</p>
            <p class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-sm">
              <template v-if="attempt.english_score !== null">
                <span v-for="s in scores" :key="s.key">
                  <span class="text-base-content/60">{{ t(s.label) }}</span>
                  <span class="ml-1 font-semibold tabular-nums">{{ attempt[s.key] }}</span>
                  <span
                    v-if="change(attempt, s.key)"
                    class="ml-1 tabular-nums"
                    :class="change(attempt, s.key)! > 0 ? 'text-success' : 'text-error'"
                  >
                    {{ change(attempt, s.key)! > 0 ? '▲' : '▼' }}{{ Math.abs(change(attempt, s.key)!) }}
                  </span>
                </span>
              </template>
              <span v-else class="text-base-content/60">{{ t('history.notScored') }}</span>
            </p>
          </div>
          <RouterLink class="btn btn-sm" :to="{ name: 'attempt', params: { id: attempt.id } }">{{ t('history.review') }}</RouterLink>
        </li>
      </ul>
    </section>
  </main>
</template>
