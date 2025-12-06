export interface ReviewItem {
  id: number
  phrase: string
  explanation: string
  dueAt: string
  isCompleted: boolean
  createdAt: string
  completedAt?: string | null
}

export interface ReviewNextResponse {
  reviewItems: ReviewItem[]
  totalCount: number
}

export type ReviewResult = 'correct' | 'incorrect'

export type ReviewProblemType = 'speaking' | 'listening' | 'phrase'

export interface ReviewProblem {
  type: ReviewProblemType
  review_item_id: number
  phrase: string
  explanation: string
  sentence?: string
  word_options?: string[]
  distractors?: string[]
  phrase_highlight?: [number, number]
}

export interface WordMatch {
  word: string
  matched: boolean
  position: number
}

export interface SpeakingEvaluationResult {
  word_matches: WordMatch[]
  score: number
  matched_count: number
  total_count: number
}

export interface ReviewEvaluationResult {
  type: ReviewProblemType
  is_correct: boolean
  speaking_result?: SpeakingEvaluationResult
  expected?: string
  review_item: ReviewItem
}
