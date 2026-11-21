<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import DifficultySelect from '../components/DifficultySelect.vue'
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
    <RouterLink class="btn btn-ghost btn-sm" to="/">← Interviews</RouterLink>
    <header class="py-4">
      <h1 class="text-3xl font-bold">Add a job posting</h1>
      <p class="mt-2 text-base-content/70">
        Interview questions are written for this posting, and follow-up questions and feedback take it into account.
      </p>
    </header>

    <div v-if="error" role="alert" class="alert alert-error alert-soft mb-4">{{ error }}</div>

    <form class="card bg-base-100 shadow-sm" @submit.prevent="add">
      <div class="card-body gap-3">
        <label class="grid gap-1">
          <span class="text-sm font-medium">Link</span>
          <input v-model="url" type="url" class="input w-full" placeholder="https://…" :disabled="adding" />
          <span class="text-xs text-base-content/60">
            The posting text is extracted from the page. If a site cannot be read (for example, it needs a login),
            paste the text below instead.
          </span>
        </label>
        <div class="divider my-0 text-xs">or paste it</div>
        <label class="grid gap-1">
          <span class="text-sm font-medium">Title</span>
          <input
            v-model="title"
            class="input w-full"
            placeholder="Senior Backend Engineer at Acme"
            maxlength="200"
            :disabled="adding"
          />
        </label>
        <label class="grid gap-1">
          <span class="text-sm font-medium">Posting text</span>
          <textarea v-model="text" class="textarea h-40 w-full text-sm" :disabled="adding"></textarea>
        </label>
        <div class="card-actions items-center justify-end">
          <DifficultySelect v-model="difficulty" :disabled="adding" />
          <button class="btn btn-primary" :disabled="adding || (!url.trim() && !text.trim())">
            <span v-if="adding" class="loading loading-spinner loading-xs"></span>
            {{ adding ? 'Adding and writing questions…' : 'Add posting' }}
          </button>
        </div>
      </div>
    </form>
  </main>
</template>
