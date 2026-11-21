<script setup lang="ts">
import { computed } from 'vue'
import { total, type SubScore } from '../scores'

const props = defineProps<{
  title: string
  scores: SubScore[]
  summary: string
  /** Score of the previous attempt at the same question, to show the change. */
  previous?: number | null
}>()

// The headline score is the plain average of the sub-scores shown below it.
const score = computed(() => total(props.scores))
const change = computed(() => (props.previous == null ? null : score.value - props.previous))

const tone = (value: number) => (value >= 75 ? 'success' : value >= 60 ? 'warning' : 'error')
const textClass = { success: 'text-success', warning: 'text-warning', error: 'text-error' }
const barClass = { success: 'progress-success', warning: 'progress-warning', error: 'progress-error' }
</script>

<template>
  <div class="card bg-base-100 shadow-sm">
    <div class="card-body gap-4">
      <div class="flex items-center gap-4">
        <div
          class="radial-progress shrink-0 text-xl font-bold"
          :class="textClass[tone(score)]"
          :style="{ '--value': score, '--size': '5rem', '--thickness': '0.5rem' }"
          role="progressbar"
          :aria-valuenow="score"
          :aria-label="`${title} score`"
        >
          {{ score }}
        </div>
        <div class="grow">
          <h3 class="card-title">
            {{ title }}
            <span
              v-if="change !== null"
              class="badge badge-soft"
              :class="change > 0 ? 'badge-success' : change < 0 ? 'badge-error' : ''"
            >
              {{ change > 0 ? `+${change}` : change }} vs last time
            </span>
          </h3>
          <div v-for="s in scores" :key="s.label" class="flex items-center gap-2 text-sm">
            <span class="w-28 shrink-0 text-base-content/70">{{ s.label }}</span>
            <progress class="progress grow" :class="barClass[tone(s.value)]" :value="s.value" max="100"></progress>
            <span class="w-7 text-right tabular-nums">{{ s.value }}</span>
          </div>
        </div>
      </div>
      <p class="text-sm">{{ summary }}</p>
      <slot />
    </div>
  </div>
</template>
