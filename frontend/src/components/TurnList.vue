<script setup lang="ts">
import type { Turn } from '../types'

defineProps<{
  turns: Turn[]
  /** File name prefix for downloaded recordings. */
  downloadPrefix: string
}>()
</script>

<template>
  <div class="grid gap-3">
    <div v-for="(turn, i) in turns" :key="i" class="card bg-base-100 shadow-sm">
      <div class="card-body gap-2">
        <p class="font-semibold">{{ turn.question }}</p>
        <p class="text-base-content/70">{{ turn.answer || '(no speech recognized)' }}</p>

        <div v-if="turn.delivery" class="flex flex-wrap items-center gap-2 text-sm">
          <span class="badge badge-soft">Clarity {{ turn.delivery.clarity }}</span>
          <span v-if="turn.delivery.wordsPerMinute" class="badge badge-soft">
            {{ turn.delivery.wordsPerMinute }} words/min
          </span>
          <template v-if="turn.delivery.unclearWords.length">
            <span class="text-base-content/60">Unclear:</span>
            <span v-for="w in turn.delivery.unclearWords" :key="w" class="badge badge-warning badge-soft">
              {{ w }}
            </span>
          </template>
        </div>

        <div v-if="turn.recordingUrl && turn.hasVideo" class="collapse collapse-arrow bg-base-200">
          <input type="checkbox" />
          <div class="collapse-title text-sm">Watch recording</div>
          <div class="collapse-content">
            <video
              class="w-full max-w-lg rounded-box"
              :src="turn.recordingUrl"
              controls
              playsinline
              preload="metadata"
            ></video>
            <a class="btn btn-sm mt-2" :href="turn.recordingUrl" :download="`${downloadPrefix}-${i + 1}.webm`">
              Download
            </a>
          </div>
        </div>
        <div v-else-if="turn.recordingUrl" class="flex flex-wrap items-center gap-2">
          <audio class="h-10 grow" :src="turn.recordingUrl" controls preload="metadata"></audio>
          <a class="btn btn-sm" :href="turn.recordingUrl" :download="`${downloadPrefix}-${i + 1}.webm`">Download</a>
        </div>
      </div>
    </div>
  </div>
</template>
