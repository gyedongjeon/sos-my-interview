import { describe, expect, it } from 'vitest'
import { contentScores, englishScores, mean, total } from './scores'
import type { Feedback, SpeakingFeedback } from './types'

const feedback: Feedback = {
  english: { grammar: 70, vocabulary: 65, naturalness: 60, summary: '', corrections: [] },
  content: { relevance: 80, structure: 75, specificity: 55, summary: '', strengths: [], improvements: [] },
  better_answer: '',
}
const speaking: SpeakingFeedback = { pronunciation: 90, intonation: 80, stress: 70, summary: '', tips: [] }

const labels = (scores: { label: string }[]) => scores.map((s) => s.label)

describe('mean', () => {
  it('rounds to a whole number', () => {
    expect(mean([70, 65, 60])).toBe(65)
    expect(mean([70, 71])).toBe(71)
  })

  it('is 0 when there is nothing to average', () => {
    expect(mean([])).toBe(0)
  })
})

describe('englishScores', () => {
  it('puts how it sounded before the sentences when the audio was scored', () => {
    const scores = englishScores(feedback, speaking, 50)
    expect(labels(scores)).toEqual(['Pronunciation', 'Intonation', 'Stress', 'Grammar', 'Vocabulary', 'Naturalness'])
    expect(scores[0].value).toBe(90)
  })

  it('uses recognition clarity as pronunciation when no model heard the audio', () => {
    const scores = englishScores(feedback, null, 82)
    expect(labels(scores)).toEqual(['Pronunciation', 'Grammar', 'Vocabulary', 'Naturalness'])
    expect(scores[0].value).toBe(82)
  })

  it('scores the sentences alone when there is no audio information', () => {
    expect(labels(englishScores(feedback, null, null))).toEqual(['Grammar', 'Vocabulary', 'Naturalness'])
  })

  it('keeps a clarity of 0 instead of treating it as missing', () => {
    expect(englishScores(feedback, null, 0)[0]).toEqual({ label: 'Pronunciation', value: 0 })
  })
})

describe('total', () => {
  it('is the average of the sub-scores', () => {
    expect(total(contentScores(feedback))).toBe(70)
    expect(total(englishScores(feedback, speaking, null))).toBe(73)
  })
})
