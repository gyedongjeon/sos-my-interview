<script setup lang="ts">
import { onMounted } from 'vue'
import QuestionList from '../components/QuestionList.vue'
import { t } from '../i18n'
import { useInterviewStore } from '../stores/interview'
import MorseSignal from '../components/MorseSignal.vue'

const store = useInterviewStore()

onMounted(() => {
  store.load(true)
  store.loadAttempts()
})
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <RouterLink class="btn btn-ghost btn-sm" to="/">{{ t('common.backToInterviews') }}</RouterLink>
    <header class="py-4">
      <h1 class="text-3xl font-bold">{{ t('common.commonQuestions') }}</h1>
      <p class="mt-2 text-base-content/70">{{ t('commonView.intro') }}</p>
    </header>

    <div v-if="store.loading" class="flex justify-center py-16">
      <MorseSignal animated />
    </div>
    <div v-else-if="store.error" role="alert" class="alert alert-error">{{ store.error }}</div>
    <QuestionList v-else :title="t('questions.title')" :questions="store.common" />
  </main>
</template>
