<script setup lang="ts">
import { ref, watch } from 'vue'

// Upload-or-paste editor for one document (a résumé or a cover letter).
const props = defineProps<{
  /** Saved text, or null when the document is not set. */
  text: string | null
  filename: string | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  /** FormData with either `file` or `text`, ready to send to the backend. */
  save: [body: FormData]
  remove: []
}>()

const draft = ref(props.text ?? '')
watch(
  () => props.text,
  (text) => (draft.value = text ?? ''),
)

function upload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = '' // Allow picking the same file again.
  if (!file) return
  const body = new FormData()
  body.append('file', file)
  emit('save', body)
}

function saveText() {
  const body = new FormData()
  body.append('text', draft.value)
  emit('save', body)
}
</script>

<template>
  <div class="grid gap-3">
    <input
      type="file"
      class="file-input file-input-sm w-full"
      accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
      aria-label="Upload a PDF, .txt, or .md file"
      :disabled="disabled"
      @change="upload"
    />
    <textarea
      v-model="draft"
      class="textarea h-48 w-full font-mono text-sm"
      placeholder="Upload a PDF, .txt, or .md file above, or paste the text here."
      :disabled="disabled"
    ></textarea>
    <div class="flex flex-wrap items-center justify-between gap-2">
      <p class="text-sm text-base-content/60">{{ text === null ? '' : (filename ?? 'Pasted text') }}</p>
      <div class="flex gap-2">
        <button v-if="text !== null" class="btn btn-error btn-outline btn-sm" :disabled="disabled" @click="emit('remove')">
          Remove
        </button>
        <button
          class="btn btn-primary btn-sm"
          :disabled="disabled || !draft.trim() || draft === text"
          @click="saveText"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>
