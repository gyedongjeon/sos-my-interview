import { t } from './i18n'
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
        { label: t('score.pronunciation'), value: speaking.pronunciation },
        { label: t('score.intonation'), value: speaking.intonation },
        { label: t('score.stress'), value: speaking.stress },
      ]
    : clarity !== null
      ? [{ label: t('score.pronunciation'), value: clarity }]
      : []
  return [
    ...spoken,
    { label: t('score.grammar'), value: feedback.english.grammar },
    { label: t('score.vocabulary'), value: feedback.english.vocabulary },
    { label: t('score.naturalness'), value: feedback.english.naturalness },
  ]
}

export function contentScores(feedback: Feedback): SubScore[] {
  return [
    { label: t('score.relevance'), value: feedback.content.relevance },
    { label: t('score.structure'), value: feedback.content.structure },
    { label: t('score.specificity'), value: feedback.content.specificity },
  ]
}
