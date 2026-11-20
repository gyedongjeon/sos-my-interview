<script setup lang="ts">
import { onMounted } from 'vue'
import { useInterviewStore } from '../stores/interview'

const store = useInterviewStore()
onMounted(() => store.load())
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <header class="py-8">
      <h1 class="text-4xl font-bold">Deep Dive Interview</h1>
      <p class="mt-3 text-base-content/70">
        Pick a question, answer it out loud on a video call, then take follow-up questions that dig into what you said.
      </p>
    </header>

    <div v-if="store.loading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>

    <ul v-else class="list rounded-box bg-base-100 shadow-sm">
      <li class="p-4 pb-2 text-xs tracking-wide opacity-60">Common questions</li>
      <li v-for="(q, i) in store.questions" :key="q.id" class="list-row items-center">
        <div class="w-6 text-right tabular-nums opacity-50">{{ i + 1 }}</div>
        <div class="list-col-grow font-medium">{{ q.text }}</div>
        <span v-if="store.isAnswered(q.id)" class="badge badge-success badge-soft">Answered</span>
        <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'interview', params: { id: q.id } }">
          {{ store.isAnswered(q.id) ? 'Retry' : 'Answer' }}
        </RouterLink>
      </li>
    </ul>
  </main>
</template>
