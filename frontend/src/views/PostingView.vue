<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import DifficultySelect from '../components/DifficultySelect.vue'
import DocumentEditor from '../components/DocumentEditor.vue'
import QuestionList from '../components/QuestionList.vue'
import { formatDay } from '../dates'
import { t } from '../i18n'
import { useInterviewStore } from '../stores/interview'
import type { Difficulty, Posting } from '../types'
import MorseSignal from '../components/MorseSignal.vue'

const props = defineProps<{ id: number }>()

const route = useRoute()
const router = useRouter()
const store = useInterviewStore()

const posting = ref<Posting | null>(null)
const error = ref('')
const notice = ref(typeof route.query.warning === 'string' ? route.query.warning : '')
const busy = ref(false)
const difficulty = ref<Difficulty>('easy')
const draft = ref<{ title: string; text: string } | null>(null)
// Whether the "résumé for this posting" editor is open before anything is saved in it.
const ownResume = ref(false)

type DocumentKind = 'resume' | 'cover_letter'

const saveDocument = (kind: DocumentKind, body: FormData) =>
  run(async () => {
    posting.value = await api<Posting>(`/postings/${props.id}/documents/${kind}`, { method: 'PUT', body })
    notice.value = t('posting.documentSaved')
  })

const removeDocument = (kind: DocumentKind) =>
  run(async () => {
    posting.value = await api<Posting>(`/postings/${props.id}/documents/${kind}`, { method: 'DELETE' })
    if (kind === 'resume') ownResume.value = false
  })

// Switching back to the common résumé discards the posting's own one, so confirm first.
function useCommonResume() {
  if (posting.value?.resume_text == null) {
    ownResume.value = false
    return
  }
  if (window.confirm(t('posting.confirmCommonResume'))) removeDocument('resume')
}

// Runs a request that changes the posting; errors are shown at the top of the page.
async function run(action: () => Promise<void>) {
  error.value = ''
  notice.value = ''
  busy.value = true
  try {
    await action()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    busy.value = false
  }
}

const rewrite = () => {
  const answered = store.forPosting(props.id).some((q) => store.attemptsFor(q.id).length)
  const warning = answered
    ? t('posting.confirmRewriteAnswered')
    : t('posting.confirmRewrite')
  if (store.forPosting(props.id).length && !window.confirm(warning)) return
  return run(async () => {
    posting.value = await api<Posting>(`/postings/${props.id}/questions?difficulty=${difficulty.value}`, {
      method: 'POST',
    })
    await store.load(true)
  })
}

const saveEdit = () =>
  run(async () => {
    if (!draft.value) return
    posting.value = await api<Posting>(`/postings/${props.id}`, { method: 'PUT', json: draft.value })
    draft.value = null
  })

const remove = () => {
  if (!window.confirm(t('posting.confirmDelete'))) return
  return run(async () => {
    await api(`/postings/${props.id}`, { method: 'DELETE' })
    router.push('/')
  })
}

onMounted(async () => {
  try {
    const [loaded] = await Promise.all([
      api<Posting>(`/postings/${props.id}`),
      store.load(true),
      store.loadAttempts(),
    ])
    posting.value = loaded
    ownResume.value = loaded.resume_text !== null
  } catch (e) {
    error.value = (e as Error).message
  }
})
</script>

<template>
  <main class="mx-auto max-w-3xl p-4 sm:p-8">
    <RouterLink class="btn btn-ghost btn-sm" to="/">{{ t('common.backToInterviews') }}</RouterLink>

    <div v-if="error" role="alert" class="alert alert-error alert-soft my-4">{{ error }}</div>
    <div v-if="notice" role="status" class="alert alert-info alert-soft my-4">{{ notice }}</div>

    <div v-if="!posting && !error" class="flex justify-center py-16">
      <MorseSignal animated />
    </div>

    <template v-if="posting">
      <header class="py-4">
        <h1 class="text-3xl font-bold">{{ posting.title }}</h1>
        <p class="mt-2 text-sm text-base-content/60">
          {{ t('common.added', { date: formatDay(posting.created_at) }) }}
          <template v-if="posting.url">
            · <a class="link" :href="posting.url" target="_blank" rel="noopener noreferrer">{{ t('posting.open') }}</a>
          </template>
        </p>
      </header>

      <div class="card bg-base-100 shadow-sm">
        <div class="card-body gap-3">
          <template v-if="draft">
            <input v-model="draft.title" class="input w-full" maxlength="200" :aria-label="t('common.title')" />
            <textarea v-model="draft.text" class="textarea h-64 w-full text-sm" :aria-label="t('common.postingText')"></textarea>
            <div class="card-actions justify-end">
              <button class="btn btn-sm" :disabled="busy" @click="draft = null">{{ t('common.cancel') }}</button>
              <button
                class="btn btn-primary btn-sm"
                :disabled="busy || !draft.title.trim() || !draft.text.trim()"
                @click="saveEdit"
              >
                {{ t('common.save') }}
              </button>
            </div>
          </template>
          <template v-else>
            <div class="collapse collapse-arrow bg-base-200">
              <input type="checkbox" />
              <div class="collapse-title text-sm">{{ t('common.postingText') }}</div>
              <div class="collapse-content">
                <p class="whitespace-pre-wrap text-sm">{{ posting.text }}</p>
              </div>
            </div>
            <div class="card-actions justify-end">
              <button class="btn btn-error btn-outline btn-sm" :disabled="busy" @click="remove">{{ t('common.delete') }}</button>
              <button
                class="btn btn-sm"
                :disabled="busy"
                @click="draft = { title: posting.title, text: posting.text }"
              >
                {{ t('common.edit') }}
              </button>
            </div>
          </template>
        </div>
      </div>

      <div class="card mt-4 bg-base-100 shadow-sm">
        <div class="card-body gap-4">
          <div>
            <h2 class="card-title text-base">{{ t('posting.application') }}</h2>
            <p class="text-sm text-base-content/60">{{ t('posting.applicationBody') }}</p>
          </div>

          <fieldset class="grid gap-2">
            <legend class="mb-1 text-sm font-medium">{{ t('nav.resume') }}</legend>
            <label class="flex items-center gap-2 text-sm">
              <input
                type="radio"
                class="radio radio-sm"
                name="resume-source"
                :checked="!ownResume"
                :disabled="busy"
                @change="useCommonResume"
              />
              {{ t('posting.useCommon') }}
              <RouterLink class="link text-base-content/60" to="/resume">{{ t('posting.view') }}</RouterLink>
            </label>
            <label class="flex items-center gap-2 text-sm">
              <input
                type="radio"
                class="radio radio-sm"
                name="resume-source"
                :checked="ownResume"
                :disabled="busy"
                @change="ownResume = true"
              />
              {{ t('posting.useOwn') }}
            </label>
            <DocumentEditor
              v-if="ownResume"
              :text="posting.resume_text"
              :filename="posting.resume_filename"
              :disabled="busy"
              @save="saveDocument('resume', $event)"
              @remove="removeDocument('resume')"
            />
          </fieldset>

          <div class="grid gap-2">
            <h3 class="text-sm font-medium">{{ t('posting.coverLetter') }} <span class="font-normal text-base-content/60">{{ t('common.optional') }}</span></h3>
            <DocumentEditor
              :text="posting.cover_letter_text"
              :filename="posting.cover_letter_filename"
              :disabled="busy"
              @save="saveDocument('cover_letter', $event)"
              @remove="removeDocument('cover_letter')"
            />
          </div>
        </div>
      </div>

      <div class="mt-6 mb-2 flex flex-wrap items-center justify-end gap-2">
        <DifficultySelect v-model="difficulty" :disabled="busy" />
        <button class="btn btn-sm" :disabled="busy" @click="rewrite">
          <span v-if="busy" class="loading loading-spinner loading-xs"></span>
          {{ store.forPosting(id).length ? t('posting.rewrite') : t('posting.write') }}
        </button>
      </div>
      <QuestionList :title="t('questions.forPosting')" :questions="store.forPosting(id)" />
    </template>
  </main>
</template>
