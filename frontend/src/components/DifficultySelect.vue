<script setup lang="ts">
import type { Difficulty } from '../types'

const model = defineModel<Difficulty>({ required: true })
defineProps<{ disabled?: boolean }>()

const options: { value: Difficulty; label: string; hint: string }[] = [
  { value: 'easy', label: 'Easy', hint: 'short warm-up questions' },
  { value: 'standard', label: 'Standard', hint: 'a first-round interview' },
  { value: 'hard', label: 'Hard', hint: 'a demanding final round' },
]
</script>

<template>
  <select v-model="model" class="select select-sm w-auto" :disabled="disabled" aria-label="Question difficulty">
    <option v-for="o in options" :key="o.value" :value="o.value">{{ o.label }}: {{ o.hint }}</option>
  </select>
</template>
