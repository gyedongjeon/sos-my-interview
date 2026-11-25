<script setup lang="ts">
import { computed } from 'vue'
import ScoreCard from './ScoreCard.vue'
import { t } from '../i18n'
import { contentScores, englishScores } from '../scores'
import type { Feedback, SpeakingFeedback } from '../types'

const props = defineProps<{
  feedback: Feedback
  speaking: SpeakingFeedback | null
  /** Average Whisper clarity, used as the pronunciation score when `speaking` is missing. */
  clarity: number | null
  previousEnglish?: number | null
  previousContent?: number | null
}>()

defineEmits<{ listen: [text: string] }>()

const english = computed(() => englishScores(props.feedback, props.speaking, props.clarity))
const content = computed(() => contentScores(props.feedback))
</script>

<template>
  <section class="grid gap-3">
    <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
      <ScoreCard :title="t('score.english')" :scores="english" :summary="feedback.english.summary" :previous="previousEnglish">
        <div v-if="speaking" class="grid gap-2">
          <h4 class="text-sm font-semibold">{{ t('feedback.speaking') }}</h4>
          <p class="text-sm">{{ speaking.summary }}</p>
          <ul v-if="speaking.tips.length" class="grid gap-2">
            <li v-for="(tip, i) in speaking.tips" :key="i" class="rounded-box bg-base-200 p-3 text-sm">
              <span class="font-medium">{{ tip.phrase }}</span>
              <p class="text-base-content/70">{{ tip.advice }}</p>
            </li>
          </ul>
        </div>
        <div v-if="feedback.english.corrections.length" class="grid gap-2">
          <h4 class="text-sm font-semibold">{{ t('feedback.sentences') }}</h4>
          <ul class="grid gap-2">
            <li v-for="(c, i) in feedback.english.corrections" :key="i" class="rounded-box bg-base-200 p-3 text-sm">
              <p class="text-error line-through">{{ c.original }}</p>
              <p class="font-medium text-success">{{ c.improved }}</p>
              <p class="mt-1 text-base-content/70">{{ c.explanation }}</p>
            </li>
          </ul>
        </div>
      </ScoreCard>

      <ScoreCard :title="t('score.content')" :scores="content" :summary="feedback.content.summary" :previous="previousContent">
        <div v-if="feedback.content.strengths.length">
          <h4 class="text-sm font-semibold text-success">{{ t('feedback.strengths') }}</h4>
          <ul class="list-disc pl-5 text-sm">
            <li v-for="(s, i) in feedback.content.strengths" :key="i">{{ s }}</li>
          </ul>
        </div>
        <div v-if="feedback.content.improvements.length">
          <h4 class="text-sm font-semibold text-warning">{{ t('feedback.improvements') }}</h4>
          <ul class="list-disc pl-5 text-sm">
            <li v-for="(s, i) in feedback.content.improvements" :key="i">{{ s }}</li>
          </ul>
        </div>
      </ScoreCard>
    </div>

    <div class="card bg-base-100 shadow-sm">
      <div class="card-body gap-2">
        <div class="flex items-center justify-between gap-2">
          <h3 class="card-title text-base">{{ t('feedback.better') }}</h3>
          <button class="btn btn-sm" @click="$emit('listen', feedback.better_answer)">{{ t('feedback.listen') }}</button>
        </div>
        <p class="text-base-content/80">{{ feedback.better_answer }}</p>
        <slot name="better-answer-actions" />
      </div>
    </div>
  </section>
</template>
