import { apiRequest } from '@/lib/api-client'

export type PlacementQuestionType = 'listening' | 'speaking'

export interface PlacementQuestion {
  id: number
  type: PlacementQuestionType
  prompt: string
  scenario_hint?: string
}

export interface PlacementQuestionsResponse {
  questions: PlacementQuestion[]
}

export interface PlacementAnswerPayload {
  question_id: number
  self_score: number
}

export interface PlacementSubmitResult {
  score: number
  max_score: number
  placement_level: 'beginner' | 'intermediate' | 'advanced'
  placement_completed_at: string
}

export async function fetchPlacementQuestions(): Promise<PlacementQuestion[]> {
  const result = await apiRequest<PlacementQuestionsResponse>('/placement/questions', 'GET')
  return result.questions
}

export async function submitPlacementAnswers(
  answers: PlacementAnswerPayload[],
): Promise<PlacementSubmitResult> {
  return apiRequest<PlacementSubmitResult>('/placement/submit', 'POST', {
    answers,
  })
}


