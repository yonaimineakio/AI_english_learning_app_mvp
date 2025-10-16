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

