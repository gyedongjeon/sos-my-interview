import type { Feedback, SpeakingFeedback } from './types'

export interface SubScore {
  label: string
  value: number
}

export const mean = (values: number[]) =>
  values.length ? Math.round(values.reduce((a, b) => a + b, 0) / values.length) : 0

export const total = (scores: SubScore[]) => mean(scores.map((s) => s.value))

/**
 * English sub-scores: how it sounded first, then the sentences. When no model listened to
 * the audio, Whisper's recognition confidence (`clarity`) stands in for pronunciation.
 */
export function englishScores(
  feedback: Feedback,
  speaking: SpeakingFeedback | null,
  clarity: number | null,
): SubScore[] {
  const spoken: SubScore[] = speaking
    ? [
        { label: 'Pronunciation', value: speaking.pronunciation },
        { label: 'Intonation', value: speaking.intonation },
        { label: 'Stress', value: speaking.stress },
      ]
    : clarity !== null
      ? [{ label: 'Pronunciation', value: clarity }]
      : []
  return [
    ...spoken,
    { label: 'Grammar', value: feedback.english.grammar },
    { label: 'Vocabulary', value: feedback.english.vocabulary },
    { label: 'Naturalness', value: feedback.english.naturalness },
  ]
}

export function contentScores(feedback: Feedback): SubScore[] {
  return [
    { label: 'Relevance', value: feedback.content.relevance },
    { label: 'Structure', value: feedback.content.structure },
    { label: 'Specificity', value: feedback.content.specificity },
  ]
}
