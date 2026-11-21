<script setup lang="ts">
import { onMounted } from 'vue'
import { LANGUAGES, useSettingsStore } from './stores/settings'

const settings = useSettingsStore()
onMounted(() => settings.load())
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
    <RouterView />
  </div>
</template>
