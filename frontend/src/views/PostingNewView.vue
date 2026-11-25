<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import DifficultySelect from '../components/DifficultySelect.vue'
import { t } from '../i18n'
import type { Difficulty, Posting } from '../types'

const router = useRouter()
const url = ref('')
const title = ref('')
const text = ref('')
const difficulty = ref<Difficulty>('easy')
const adding = ref(false)
const error = ref('')

async function add() {
  error.value = ''
  adding.value = true
  try {
    const posting = await api<Posting>('/postings', {
      method: 'POST',
      json: { url: url.value.trim() || null, title: title.value, text: text.value, difficulty: difficulty.value },
    })
    // A warning means the posting was saved but its questions were not written; its page says so.
    router.push({ name: 'posting', params: { id: posting.id }, query: posting.warning ? { warning: posting.warning } : {} })
  } catch (e) {
    error.value = (e as Error).message
    adding.value = false
  }
}
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <RouterLink class="btn btn-ghost btn-sm" to="/">{{ t('common.backToInterviews') }}</RouterLink>
    <header class="py-4">
      <h1 class="text-3xl font-bold">{{ t('home.addPosting') }}</h1>
      <p class="mt-2 text-base-content/70">{{ t('postingNew.intro') }}</p>
    </header>

    <div v-if="error" role="alert" class="alert alert-error alert-soft mb-4">{{ error }}</div>

    <form class="card bg-base-100 shadow-sm" @submit.prevent="add">
      <div class="card-body gap-3">
        <label class="grid gap-1">
          <span class="text-sm font-medium">{{ t('postingNew.link') }}</span>
          <input v-model="url" type="url" class="input w-full" placeholder="https://…" :disabled="adding" />
          <span class="text-xs text-base-content/60">{{ t('postingNew.linkHelp') }}</span>
        </label>
        <div class="divider my-0 text-xs">{{ t('postingNew.orPaste') }}</div>
        <label class="grid gap-1">
          <span class="text-sm font-medium">{{ t('common.title') }}</span>
          <input
            v-model="title"
            class="input w-full"
            :placeholder="t('postingNew.titlePlaceholder')"
            maxlength="200"
            :disabled="adding"
          />
        </label>
        <label class="grid gap-1">
          <span class="text-sm font-medium">{{ t('common.postingText') }}</span>
          <textarea v-model="text" class="textarea h-40 w-full text-sm" :disabled="adding"></textarea>
        </label>
        <div class="card-actions items-center justify-end">
          <DifficultySelect v-model="difficulty" :disabled="adding" />
          <button class="btn btn-primary" :disabled="adding || (!url.trim() && !text.trim())">
            <span v-if="adding" class="loading loading-spinner loading-xs"></span>
            {{ adding ? t('postingNew.adding') : t('postingNew.add') }}
          </button>
        </div>
      </div>
    </form>
  </main>
</template>
