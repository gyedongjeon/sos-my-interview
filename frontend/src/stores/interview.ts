import { defineStore } from 'pinia'
import { api } from '../api'
import type { AttemptSummary, Question } from '../types'

interface State {
  questions: Question[]
  loaded: boolean
  loading: boolean
  error: string | null
  /** Saved attempts, newest first. */
  attempts: AttemptSummary[]
}

export const useInterviewStore = defineStore('interview', {
  state: (): State => ({
    questions: [],
    loaded: false,
    loading: false,
    error: null,
    attempts: [],
  }),
  getters: {
    common: (s): Question[] => s.questions.filter((q) => q.posting_id === null),
    forPosting: (s) => (postingId: number): Question[] => s.questions.filter((q) => q.posting_id === postingId),
    byId: (s) => (id: number): Question | null => s.questions.find((q) => q.id === id) ?? null,
    attemptsFor: (s) => (questionId: number): AttemptSummary[] =>
      s.attempts.filter((a) => a.question_id === questionId),
  },
  actions: {
    // Questions change when job postings do, so pages that list them pass force = true.
    async load(force = false) {
      if (this.loading || (this.loaded && !force)) return
      this.loading = !this.loaded
      this.error = null
      try {
        this.questions = await api<Question[]>('/questions')
        this.loaded = true
      } catch (e) {
        this.error = `Failed to load questions: ${(e as Error).message}`
      } finally {
        this.loading = false
      }
    },
    async loadAttempts() {
      try {
        this.attempts = await api<AttemptSummary[]>('/attempts')
      } catch (e) {
        this.error = `Failed to load history: ${(e as Error).message}`
      }
    },
  },
})
