<script setup lang="ts">
import { onMounted } from 'vue'
import QuestionList from '../components/QuestionList.vue'
import { useInterviewStore } from '../stores/interview'

const store = useInterviewStore()

onMounted(() => {
  store.load(true)
  store.loadAttempts()
})
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <RouterLink class="btn btn-ghost btn-sm" to="/">← Interviews</RouterLink>
    <header class="py-4">
      <h1 class="text-3xl font-bold">Common questions</h1>
      <p class="mt-2 text-base-content/70">Questions that come up in almost every interview.</p>
    </header>

    <div v-if="store.loading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>
    <QuestionList v-else title="Questions" :questions="store.common" />
  </main>
</template>
