<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import MorseSignal from '../components/MorseSignal.vue'
import { formatDay } from '../dates'
import { t } from '../i18n'
import { useInterviewStore } from '../stores/interview'
import type { Posting } from '../types'

const store = useInterviewStore()
const postings = ref<Posting[]>([])
const loading = ref(true)
const error = ref('')

// Number of a list's questions that have been answered at least once.
const answeredCount = (questionIds: number[]) =>
  questionIds.filter((id) => store.attemptsFor(id).length).length

// Every list that can be practised: one per job posting, then the common questions.
const lists = computed(() => [
  ...postings.value.map((p) => ({
    key: `posting-${p.id}`,
    to: { name: 'posting', params: { id: p.id } },
    title: p.title,
    note: t('common.added', { date: formatDay(p.created_at) }),
    answered: answeredCount(store.forPosting(p.id).map((q) => q.id)),
    total: p.question_count,
  })),
  {
    key: 'common',
    to: { name: 'common' },
    title: t('common.commonQuestions'),
    note: t('home.commonNote'),
    answered: answeredCount(store.common.map((q) => q.id)),
    total: store.common.length,
  },
])

onMounted(async () => {
  try {
    const [list] = await Promise.all([api<Posting[]>('/postings'), store.load(true), store.loadAttempts()])
    postings.value = list
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <header class="flex flex-wrap items-end justify-between gap-4 py-8">
      <div>
        <MorseSignal />
        <h1 class="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl">
          {{ t('home.headline1') }}<br />
          <span class="text-primary">{{ t('home.headline2') }}</span>
        </h1>
        <p class="mt-3 text-base-content/70">{{ t('home.intro') }}</p>
      </div>
      <RouterLink class="btn btn-primary" :to="{ name: 'posting-new' }">{{ t('home.addPosting') }}</RouterLink>
    </header>

    <div v-if="loading" class="flex justify-center py-16">
      <MorseSignal animated />
    </div>
    <div v-else-if="error || store.error" role="alert" class="alert alert-error">{{ error || store.error }}</div>

    <div v-else class="grid gap-3">
      <RouterLink
        v-for="list in lists"
        :key="list.key"
        class="card card-border bg-base-100 transition hover:border-primary"
        :to="list.to"
      >
        <div class="card-body flex-row items-center gap-4">
          <div class="grow">
            <h2 class="card-title text-lg">{{ list.title }}</h2>
            <p class="text-sm text-base-content/60">
              {{ list.note }} · {{ t('home.answered', { answered: list.answered, total: list.total }) }}
            </p>
            <progress
              class="progress progress-primary mt-2 h-1.5"
              :value="list.answered"
              :max="list.total || 1"
              aria-hidden="true"
            ></progress>
          </div>
          <span aria-hidden="true" class="text-2xl text-primary">›</span>
        </div>
      </RouterLink>
    </div>
  </main>
</template>
