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

export interface SavedPhrase {
  id: number
  phrase: string
  explanation: string
  originalInput?: string | null
  sessionId?: number | null
  roundIndex?: number | null
  convertedToReviewId?: number | null
  createdAt: string
}

export interface SavedPhrasesListResponse {
  savedPhrases: SavedPhrase[]
  totalCount: number
}

export interface SavedPhraseCreate {
  phrase: string
  explanation: string
  originalInput?: string
  sessionId?: number
  roundIndex?: number
}

export interface ReviewStats {
  totalItems: number
  completedItems: number
  completionRate: number
}

export interface ConvertToReviewResponse {
  savedPhraseId: number
  reviewItem: ReviewItem
}

