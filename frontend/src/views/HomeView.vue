<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { formatDay } from '../dates'
import { useInterviewStore } from '../stores/interview'
import type { Posting } from '../types'

const store = useInterviewStore()
const postings = ref<Posting[]>([])
const loading = ref(true)
const error = ref('')

// Number of a list's questions that have been answered at least once.
const answeredCount = (questionIds: number[]) =>
  questionIds.filter((id) => store.attemptsFor(id).length).length

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
    <header class="flex flex-wrap items-end justify-between gap-3 py-6">
      <div>
        <h1 class="text-3xl font-bold">Interviews</h1>
        <p class="mt-2 text-base-content/70">Pick the company you are preparing for, or warm up with common questions.</p>
      </div>
      <RouterLink class="btn btn-primary" :to="{ name: 'posting-new' }">Add a job posting</RouterLink>
    </header>

    <div v-if="loading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="error || store.error" role="alert" class="alert alert-error">{{ error || store.error }}</div>

    <div v-else class="grid gap-3">
      <RouterLink
        v-for="p in postings"
        :key="p.id"
        class="card bg-base-100 shadow-sm transition hover:shadow-md"
        :to="{ name: 'posting', params: { id: p.id } }"
      >
        <div class="card-body flex-row items-center justify-between gap-4">
          <div>
            <h2 class="card-title text-base">{{ p.title }}</h2>
            <p class="text-sm text-base-content/60">
              Added {{ formatDay(p.created_at) }} ·
              {{ answeredCount(store.forPosting(p.id).map((q) => q.id)) }} / {{ p.question_count }} questions answered
            </p>
          </div>
          <span aria-hidden="true" class="text-xl opacity-40">›</span>
        </div>
      </RouterLink>

      <RouterLink class="card bg-base-100 shadow-sm transition hover:shadow-md" :to="{ name: 'common' }">
        <div class="card-body flex-row items-center justify-between gap-4">
          <div>
            <h2 class="card-title text-base">Common questions</h2>
            <p class="text-sm text-base-content/60">
              Questions every interview asks ·
              {{ answeredCount(store.common.map((q) => q.id)) }} / {{ store.common.length }} questions answered
            </p>
          </div>
          <span aria-hidden="true" class="text-xl opacity-40">›</span>
        </div>
      </RouterLink>
    </div>
  </main>
</template>
