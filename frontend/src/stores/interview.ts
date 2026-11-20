import { defineStore } from 'pinia'
import type { Question } from '../types'

interface State {
  questions: Question[]
  loaded: boolean
  loading: boolean
  error: string | null
  /** Ids of questions answered at least once in this browser session. */
  answeredIds: number[]
}

export const useInterviewStore = defineStore('interview', {
  state: (): State => ({
    questions: [],
    loaded: false,
    loading: false,
    error: null,
    answeredIds: [],
  }),
  getters: {
    byId: (s) => (id: number): Question | null => s.questions.find((q) => q.id === id) ?? null,
    isAnswered: (s) => (id: number): boolean => s.answeredIds.includes(id),
  },
  actions: {
    async load(category = 'common') {
      if (this.loaded || this.loading) return
      this.loading = true
      this.error = null
      try {
        const res = await fetch(`/api/questions?category=${encodeURIComponent(category)}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.questions = (await res.json()) as Question[]
        this.loaded = true
      } catch (e) {
        this.error = `Failed to load questions: ${(e as Error).message}`
      } finally {
        this.loading = false
      }
    },
    markAnswered(id: number) {
      if (!this.answeredIds.includes(id)) this.answeredIds.push(id)
    },
  },
})
