import { apiRequest } from '@/lib/api-client'
import type {
  SavedPhrase,
  SavedPhraseCreate,
  SavedPhrasesListResponse,
  ConvertToReviewResponse,
  ReviewStats,
} from '@/types/review'

/**
 * 改善フレーズを保存する
 */
export async function createSavedPhrase(payload: SavedPhraseCreate): Promise<SavedPhrase> {
  const response = await apiRequest<{
    id: number
    user_id: number
    phrase: string
    explanation: string
    original_input?: string | null
    session_id?: number | null
    round_index?: number | null
    converted_to_review_id?: number | null
    created_at: string
  }>('/saved-phrases', 'POST', {
    phrase: payload.phrase,
    explanation: payload.explanation,
    original_input: payload.originalInput,
    session_id: payload.sessionId,
    round_index: payload.roundIndex,
  })

  return {
    id: response.id,
    phrase: response.phrase,
    explanation: response.explanation,
    originalInput: response.original_input,
    sessionId: response.session_id,
    roundIndex: response.round_index,
    convertedToReviewId: response.converted_to_review_id,
    createdAt: response.created_at,
  }
}

/**
 * 保存した表現一覧を取得する
 */
export async function fetchSavedPhrases(
  limit: number = 50,
  offset: number = 0
): Promise<SavedPhrasesListResponse> {
  const response = await apiRequest<{
    saved_phrases: Array<{
      id: number
      user_id: number
      phrase: string
      explanation: string
      original_input?: string | null
      session_id?: number | null
      round_index?: number | null
      converted_to_review_id?: number | null
      created_at: string
    }>
    total_count: number
  }>(`/saved-phrases?limit=${limit}&offset=${offset}`, 'GET')

  return {
    savedPhrases: response.saved_phrases.map((sp) => ({
      id: sp.id,
      phrase: sp.phrase,
      explanation: sp.explanation,
      originalInput: sp.original_input,
      sessionId: sp.session_id,
      roundIndex: sp.round_index,
      convertedToReviewId: sp.converted_to_review_id,
      createdAt: sp.created_at,
    })),
    totalCount: response.total_count,
  }
}

/**
 * 保存した表現を削除する
 */
export async function deleteSavedPhrase(savedPhraseId: number): Promise<void> {
  await apiRequest(`/saved-phrases/${savedPhraseId}`, 'DELETE')
}

/**
 * 保存した表現を復習アイテムに変換する
 */
export async function convertToReview(savedPhraseId: number): Promise<ConvertToReviewResponse> {
  const response = await apiRequest<{
    saved_phrase_id: number
    review_item: {
      id: number
      user_id: number
      phrase: string
      explanation: string
      due_at: string
      is_completed: boolean
      created_at: string
      completed_at?: string | null
    }
  }>(`/saved-phrases/${savedPhraseId}/convert-to-review`, 'POST')

  return {
    savedPhraseId: response.saved_phrase_id,
    reviewItem: {
      id: response.review_item.id,
      phrase: response.review_item.phrase,
      explanation: response.review_item.explanation,
      dueAt: response.review_item.due_at,
      isCompleted: response.review_item.is_completed,
      createdAt: response.review_item.created_at,
      completedAt: response.review_item.completed_at,
    },
  }
}

/**
 * 特定のセッション・ラウンドの保存状態を確認する
 */
export async function checkSavedPhrase(
  sessionId: number,
  roundIndex: number
): Promise<SavedPhrase | null> {
  try {
    const response = await apiRequest<{
      id: number
      user_id: number
      phrase: string
      explanation: string
      original_input?: string | null
      session_id?: number | null
      round_index?: number | null
      converted_to_review_id?: number | null
      created_at: string
    } | null>(`/saved-phrases/check/${sessionId}/${roundIndex}`, 'GET')

    if (!response) {
      return null
    }

    return {
      id: response.id,
      phrase: response.phrase,
      explanation: response.explanation,
      originalInput: response.original_input,
      sessionId: response.session_id,
      roundIndex: response.round_index,
      convertedToReviewId: response.converted_to_review_id,
      createdAt: response.created_at,
    }
  } catch {
    return null
  }
}

/**
 * 復習統計を取得する
 */
export async function fetchReviewStats(): Promise<ReviewStats> {
  const response = await apiRequest<{
    total_items: number
    completed_items: number
    completion_rate: number
  }>('/reviews/stats', 'GET')

  return {
    totalItems: response.total_items,
    completedItems: response.completed_items,
    completionRate: response.completion_rate,
  }
}

