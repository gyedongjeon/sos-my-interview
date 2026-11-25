<script setup lang="ts">
import { t } from '../i18n'
import type { Difficulty } from '../types'

const model = defineModel<Difficulty>({ required: true })
defineProps<{ disabled?: boolean }>()

const options: Difficulty[] = ['easy', 'standard', 'hard']
</script>

<template>
  <select v-model="model" class="select select-sm w-auto" :disabled="disabled" :aria-label="t('difficulty.label')">
    <option v-for="o in options" :key="o" :value="o">{{ t(`difficulty.${o}`) }}</option>
  </select>
</template>
