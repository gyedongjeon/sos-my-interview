<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { LANGUAGES, useSettingsStore } from './stores/settings'

const settings = useSettingsStore()
const router = useRouter()
onMounted(async () => {
  settings.load()
  await settings.loadLLM()
  // First launch: nothing works well without a model, so start on the setup page.
  if (settings.llm && !settings.llm.model) router.replace({ name: 'settings' })
})
</script>

<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <nav class="navbar bg-base-100 shadow-sm">
      <div class="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 px-2">
        <RouterLink class="btn btn-ghost text-lg" to="/">Deep Dive Interview</RouterLink>
        <ul class="menu menu-horizontal ml-auto gap-1 px-0">
          <li><RouterLink to="/" exact-active-class="menu-active">Interviews</RouterLink></li>
          <li><RouterLink to="/history" active-class="menu-active">History</RouterLink></li>
          <li><RouterLink to="/resume" active-class="menu-active">Résumé</RouterLink></li>
          <li><RouterLink to="/settings" active-class="menu-active">Settings</RouterLink></li>
        </ul>
        <label class="flex items-center gap-2 text-sm">
          <span class="text-base-content/60">Feedback in</span>
          <select
            class="select select-sm w-auto"
            :value="settings.feedbackLanguage"
            @change="settings.setFeedbackLanguage(($event.target as HTMLSelectElement).value)"
          >
            <option v-for="l in LANGUAGES" :key="l.name" :value="l.name">{{ l.label }}</option>
          </select>
        </label>
      </div>
    </nav>
    <div v-if="settings.error" role="alert" class="alert alert-error alert-soft mx-auto mt-4 max-w-3xl">
      {{ settings.error }}
    </div>
    <div
      v-if="settings.llm && !settings.llm.model && $route.name !== 'settings'"
      role="alert"
      class="alert alert-warning alert-soft mx-auto mt-4 max-w-3xl"
    >
      <span>Add an AI model and API key to get tailored questions, follow-up questions, and feedback.</span>
      <RouterLink class="btn btn-sm btn-warning" to="/settings">Open Settings</RouterLink>
    </div>
    <RouterView />
  </div>
</template>
