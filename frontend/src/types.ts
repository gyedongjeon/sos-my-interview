export interface Question {
  id: number
  category: string
  text: string
  /** The job posting a tailored question was written for; null for common questions. */
  posting_id: number | null
}

export interface Resume {
  filename: string | null
  text: string
  updated_at: string
}

export interface Posting {
  id: number
  title: string
  url: string | null
  text: string
  created_at: string
  /** Résumé written for this posting; null means the common résumé is used. */
  resume_text: string | null
  resume_filename: string | null
  cover_letter_text: string | null
  cover_letter_filename: string | null
  question_count: number
  warning: string | null
}

/** How an answer was spoken, measured from the audio by the local Whisper model. */
export interface Delivery {
  /** 0-100: how confidently the words were recognized, a proxy for clear pronunciation. */
  clarity: number
  unclearWords: string[]
  wordsPerMinute: number | null
}

/** One answered question (the picked one or a follow-up), as shown in a list. */
export interface Turn {
  question: string
  answer: string
  delivery: Delivery | null
  recordingUrl: string | null
  /** False when the camera was unavailable and only audio was recorded. */
  hasVideo: boolean
}

/** A turn of the interview in progress; keeps the audio for the speaking evaluation. */
export interface LiveTurn extends Turn {
  audio: Blob | null
}

export interface Correction {
  original: string
  improved: string
  explanation: string
}

/** English (sentences) and content feedback from the LLM. */
export interface Feedback {
  english: {
    grammar: number
    vocabulary: number
    naturalness: number
    summary: string
    corrections: Correction[]
  }
  content: {
    relevance: number
    structure: number
    specificity: number
    summary: string
    strengths: string[]
    improvements: string[]
  }
  better_answer: string
}

/** Feedback on how the answers sound, from a model that listened to the audio. */
export interface SpeakingFeedback {
  pronunciation: number
  intonation: number
  stress: number
  summary: string
  tips: { phrase: string; advice: string }[]
}

/** A saved attempt at one question. */
export interface AttemptSummary {
  id: number
  question_id: number
  question: string
  /** Title of the job posting the question belongs to; null for common questions. */
  posting_title: string | null
  /** ISO 8601 timestamp in UTC. */
  created_at: string
  english_score: number | null
  content_score: number | null
}

export interface AttemptDetail extends AttemptSummary {
  turns: {
    position: number
    question: string
    answer: string
    clarity: number | null
    unclear_words: string[]
    words_per_minute: number | null
    recording_url: string | null
    has_video: boolean
  }[]
  feedback: Feedback | null
  speaking: SpeakingFeedback | null
}

export type Difficulty = 'easy' | 'standard' | 'hard'

export type Phase = 'idle' | 'recording' | 'transcribing' | 'thinking' | 'done'
