<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { formatDay } from '../dates'
import type { Resume } from '../types'

const resume = ref<Resume | null>(null)
const text = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref(false)

function show(value: Resume | null) {
  resume.value = value
  text.value = value?.text ?? ''
}

async function save(body: FormData) {
  error.value = ''
  saved.value = false
  saving.value = true
  try {
    show(await api<Resume>('/resume', { method: 'PUT', body }))
    saved.value = true
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

function upload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = '' // Allow picking the same file again.
  if (!file) return
  const body = new FormData()
  body.append('file', file)
  save(body)
}

function saveText() {
  const body = new FormData()
  body.append('text', text.value)
  save(body)
}

async function remove() {
  if (!window.confirm('Delete your résumé?')) return
  error.value = ''
  saved.value = false
  try {
    await api('/resume', { method: 'DELETE' })
    show(null)
  } catch (e) {
    error.value = (e as Error).message
  }
}

onMounted(async () => {
  try {
    show(await api<Resume | null>('/resume'))
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <header class="py-6">
      <h1 class="text-3xl font-bold">Résumé</h1>
      <p class="mt-2 text-base-content/70">
        Your résumé is used to write questions about your experience and to judge your answers against it. It is stored
        on this computer; its text is sent to the LLM when questions and feedback are generated.
      </p>
    </header>

    <div v-if="loading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <div v-else class="card bg-base-100 shadow-sm">
      <div class="card-body gap-4">
        <div v-if="error" role="alert" class="alert alert-error alert-soft">{{ error }}</div>
        <div v-if="saved" role="status" class="alert alert-success alert-soft">Résumé saved.</div>

        <label class="grid gap-2">
          <span class="text-sm font-medium">Upload a file (PDF, .txt, or .md)</span>
          <input
            type="file"
            class="file-input w-full"
            accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
            :disabled="saving"
            @change="upload"
          />
        </label>

        <label class="grid gap-2">
          <span class="text-sm font-medium">
            {{ resume ? 'Extracted text (edit it if the extraction got something wrong)' : 'Or paste the text' }}
          </span>
          <textarea v-model="text" class="textarea h-96 w-full font-mono text-sm" :disabled="saving"></textarea>
        </label>

        <div class="flex flex-wrap items-center justify-between gap-2">
          <p class="text-sm text-base-content/60">
            <template v-if="resume">
              {{ resume.filename ?? 'Pasted text' }} · saved {{ formatDay(resume.updated_at) }}
            </template>
          </p>
          <div class="flex gap-2">
            <button v-if="resume" class="btn btn-error btn-outline" :disabled="saving" @click="remove">Delete</button>
            <button class="btn btn-primary" :disabled="saving || !text.trim()" @click="saveText">
              <span v-if="saving" class="loading loading-spinner loading-xs"></span>
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
