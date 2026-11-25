<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BrandMark from './components/BrandMark.vue'
import ModelDownloads from './components/ModelDownloads.vue'
import { t } from './i18n'
import { useModelsStore } from './stores/models'
import { useSettingsStore } from './stores/settings'

const settings = useSettingsStore()
const router = useRouter()
const LINK = 'hover:bg-neutral-content/10'
onMounted(async () => {
  // Fetch the speech models in the background, so they are there before the first answer.
  void useModelsStore().start()
  settings.load()
  await settings.loadLLM()
  // First launch: nothing works well without a model, so start on the setup page.
  if (settings.llm && !settings.llm.model) router.replace({ name: 'settings' })
})
</script>

<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <nav class="navbar bg-neutral text-neutral-content">
      <div class="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-2 px-2">
        <RouterLink class="flex items-center gap-2 px-2 font-display text-xl" to="/">
          <BrandMark class="size-7" />
          <span><span class="font-extrabold text-primary">SOS</span> <span class="font-medium">My Interview</span></span>
        </RouterLink>
        <ul class="menu menu-horizontal ml-auto gap-1 px-0">
          <li><RouterLink :class="LINK" to="/" exact-active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.interviews') }}</RouterLink></li>
          <li><RouterLink :class="LINK" to="/history" active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.history') }}</RouterLink></li>
          <li><RouterLink :class="LINK" to="/resume" active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.resume') }}</RouterLink></li>
          <li><RouterLink :class="LINK" to="/settings" active-class="bg-primary text-primary-content hover:bg-primary">{{ t('nav.settings') }}</RouterLink></li>
        </ul>
      </div>
    </nav>
    <ModelDownloads />
    <div v-if="settings.error" role="alert" class="alert alert-error alert-soft mx-auto mt-4 max-w-3xl">
      {{ settings.error }}
    </div>
    <div
      v-if="settings.llm && !settings.llm.model && $route.name !== 'settings'"
      role="alert"
      class="alert alert-warning alert-soft mx-auto mt-4 max-w-3xl"
    >
      <span>{{ t('app.needModel') }}</span>
      <RouterLink class="btn btn-sm btn-warning" to="/settings">{{ t('app.openSettings') }}</RouterLink>
    </div>
    <RouterView />
  </div>
</template>
