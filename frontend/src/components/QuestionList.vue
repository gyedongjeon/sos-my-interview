<script setup lang="ts">
import { useInterviewStore } from '../stores/interview'
import type { Question } from '../types'

defineProps<{ title: string; questions: Question[] }>()

const store = useInterviewStore()

// Most recent scored attempt at a question, if any.
const latest = (questionId: number) => store.attemptsFor(questionId).find((a) => a.english_score !== null)
</script>

<template>
  <ul class="list rounded-box bg-base-100 shadow-sm">
    <li class="p-4 pb-2 text-xs tracking-wide opacity-60">{{ title }}</li>
    <li v-if="!questions.length" class="p-4 text-sm text-base-content/60">No questions yet.</li>
    <li v-for="(q, i) in questions" :key="q.id" class="list-row items-center">
      <div class="w-6 text-right tabular-nums opacity-50">{{ i + 1 }}</div>
      <div class="list-col-grow">
        <p class="font-medium">{{ q.text }}</p>
        <p v-if="store.attemptsFor(q.id).length" class="mt-1 flex flex-wrap gap-2 text-xs">
          <span class="badge badge-sm badge-soft">{{ store.attemptsFor(q.id).length }} attempts</span>
          <template v-if="latest(q.id)">
            <span class="badge badge-sm badge-soft badge-primary">English {{ latest(q.id)?.english_score }}</span>
            <span class="badge badge-sm badge-soft badge-secondary">Content {{ latest(q.id)?.content_score }}</span>
          </template>
        </p>
      </div>
      <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'interview', params: { id: q.id } }">
        {{ store.attemptsFor(q.id).length ? 'Retry' : 'Answer' }}
      </RouterLink>
    </li>
  </ul>
</template>
