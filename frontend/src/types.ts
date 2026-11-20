export interface Question {
  id: number
  category: string
  text: string
}

/** One finished answer within the thread of a main question. */
export interface Turn {
  question: string
  answer: string
  recordingUrl: string | null
  /** False when the camera was unavailable and only audio was recorded. */
  hasVideo: boolean
}

export type Phase = 'idle' | 'recording' | 'transcribing' | 'thinking' | 'done'
