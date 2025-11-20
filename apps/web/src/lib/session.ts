import { apiRequest } from '@/lib/api-client'
import { ConversationTurn, SessionStatus, SessionSummary } from '@/types/conversation'
import type { ReviewItem, ReviewNextResponse, ReviewResult } from '@/types/review'

export interface StartSessionPayload {
  scenarioId: number
  roundTarget: number
  difficulty: string
  mode: string
}

export interface StartSessionResponse {
  session_id: number
  round_target: number
  difficulty: string
  mode: string
  // セッション開始時に表示するシナリオ別の初期AIメッセージ（任意）
  initial_ai_message?: string
  scenario: {
    id: number
    name: string
    description: string
  }
}

export async function startSession(payload: StartSessionPayload): Promise<StartSessionResponse> {
  return apiRequest('/sessions/start', 'POST', {
    scenario_id: payload.scenarioId,
    round_target: payload.roundTarget,
    difficulty: payload.difficulty,
    mode: payload.mode,
  })
}

interface TurnResponse {
  round_index: number
  ai_reply: {
    message: string
    feedback_short: string
    improved_sentence: string
    tags: string[]
    details?: {
      explanation?: string | null
      suggestions?: string[] | null
    } | null
    scores?: {
      pronunciation: number | null
      grammar: number | null
    } | null
  }
  session_status?: SessionStatus
  response_time_ms?: number
  should_end_session?: boolean
}

export async function submitTurn(
  sessionId: number,
  message: string,
): Promise<{ turn: ConversationTurn; status?: SessionStatus }> {
  const result = await apiRequest<TurnResponse>(`/sessions/${sessionId}/turn`, 'POST', {
    user_input: message,
  })

  const turn: ConversationTurn = {
    id: `${sessionId}-${result.round_index}`,
    roundIndex: result.round_index,
    userMessage: message,
    aiReply: {
      message: result.ai_reply.message ?? '',
      feedbackShort: result.ai_reply.feedback_short ?? '',
      improvedSentence: result.ai_reply.improved_sentence ?? '',
      tags: result.ai_reply.tags ?? [],
      scores: result.ai_reply.scores ?? null,
      details: result.ai_reply.details ?? null,
      createdAt: new Date().toISOString(),
    },
    createdAt: new Date().toISOString(),
    shouldEndSession: result.should_end_session ?? false,
  }

  return {
    turn,
    status: result.session_status,
  }
}

export async function fetchSessionStatus(sessionId: number): Promise<SessionStatus> {
  const result = await apiRequest<{
    session_id: number
    scenario_id: number
    initial_ai_message?: string
    scenario_name?: string
    round_target: number
    completed_rounds: number
    difficulty: string
    mode: string
    difficulty_label?: string
    mode_label?: string
    is_active: boolean
    can_extend?: boolean
    extension_offered?: boolean
  }>(`/sessions/${sessionId}/status`, 'GET')
  return {
    sessionId: result.session_id,
    scenarioId: result.scenario_id,
    initialAiMessage: result.initial_ai_message,
    scenarioName: result.scenario_name,
    roundTarget: result.round_target,
    completedRounds: result.completed_rounds,
    difficulty: result.difficulty,
    mode: result.mode,
    difficultyLabel: result.difficulty_label,
    modeLabel: result.mode_label,
    isActive: result.is_active,
    canExtend: result.can_extend ?? false,
    extensionOffered: result.extension_offered ?? false,
  }
}

export async function extendSession(sessionId: number): Promise<SessionStatus> {
  const result = await apiRequest<{
    session_id: number
    scenario_id: number
    round_target: number
    completed_rounds: number
    difficulty: string
    mode: string
    difficulty_label?: string
    mode_label?: string
    is_active: boolean
    can_extend?: boolean
    extension_offered?: boolean
  }>(`/sessions/${sessionId}/extend`, 'POST')
  return {
    sessionId: result.session_id,
    scenarioId: result.scenario_id,
    roundTarget: result.round_target,
    completedRounds: result.completed_rounds,
    difficulty: result.difficulty,
    mode: result.mode,
    difficultyLabel: result.difficulty_label,
    modeLabel: result.mode_label,
    isActive: result.is_active,
    canExtend: result.can_extend ?? false,
    extensionOffered: result.extension_offered ?? false,
  }
}

export async function endSession(sessionId: number): Promise<SessionSummary> {
  const result = await apiRequest<{
    session_id: number
    completed_rounds: number
    top_phrases: Array<{
      phrase: string
      explanation: string
      roundIndex?: number
    }>
    next_review_at?: string
    scenario_name?: string
    difficulty: string
    mode: string
  }>(`/sessions/${sessionId}/end`, 'POST')
  return {
    sessionId: result.session_id,
    completedRounds: result.completed_rounds,
    topPhrases: result.top_phrases,
    nextReviewAt: result.next_review_at,
    scenarioName: result.scenario_name,
    difficulty: result.difficulty,
    mode: result.mode,
  }
}


export async function fetchReviewItems(): Promise<ReviewNextResponse> {
  const result = await apiRequest<{
    review_items: ReviewItem[]
    total_count: number
  }>('/reviews/next', 'GET')
  return {
    reviewItems: result.review_items,
    totalCount: result.total_count,
  }
}

export async function completeReviewItem(reviewId: number, result: ReviewResult): Promise<ReviewItem> {
  const response = await apiRequest<{
    id: number
    phrase: string
    explanation: string
    due_at: string
    is_completed: boolean
    created_at: string
    completed_at?: string
  }>(`/reviews/${reviewId}/complete`, 'POST', { result })
  return {
    id: response.id,
    phrase: response.phrase,
    explanation: response.explanation,
    dueAt: response.due_at,
    isCompleted: response.is_completed,
    createdAt: response.created_at,
    completedAt: response.completed_at,
  }
}

// サマリー画面用のAPI関数
export async function fetchSessionSummary(sessionId: number): Promise<SessionSummary> {
  return endSession(sessionId)
}

export async function fetchLatestSessionSummary(): Promise<SessionSummary | null> {
  try {
    // 最新のセッションIDを取得するAPIが必要だが、現在は直接取得できない
    // セッション一覧APIが実装されていないため、暫定的にnullを返す
    return null
  } catch (error) {
    console.error('Failed to fetch latest session summary:', error)
    return null
  }
}

// 音声認識API
export interface TranscriptionResponse {
  text: string
  confidence?: number
  language?: string
  duration?: number
  alternatives?: Array<{
    text: string
    confidence?: number
  }>
}

export async function transcribeAudio(audioFile: File, language?: string): Promise<TranscriptionResponse> {
  const formData = new FormData()
  formData.append('audio_file', audioFile)
  if (language) {
    formData.append('language', language)
  }

  const result = await apiRequest<TranscriptionResponse>('/audio/transcribe', 'POST', formData)
  console.log('result', result)
  return result
}


