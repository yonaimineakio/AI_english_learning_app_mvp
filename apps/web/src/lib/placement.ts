import { apiRequest } from '@/lib/api-client'

export type PlacementQuestionType = 'listening' | 'speaking'

export interface PlacementQuestion {
  id: number
  type: PlacementQuestionType
  prompt: string
  scenario_hint?: string
  expected_text?: string
  word_options?: string[]
  distractor_words?: string[]
}

export interface PlacementQuestionsResponse {
  questions: PlacementQuestion[]
}

export interface PlacementAnswerPayload {
  question_id: number
  self_score?: number
  speaking_score?: number
  listening_correct?: boolean
}

export interface PlacementSubmitResult {
  score: number
  max_score: number
  placement_level: 'beginner' | 'intermediate' | 'advanced'
  placement_completed_at: string
}

// Speaking evaluation types
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
  expected_text: string
}

// Listening evaluation types
export interface ListeningEvaluationResult {
  correct: boolean
  expected: string
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

export async function evaluateSpeaking(
  questionId: number,
  userTranscript: string,
): Promise<SpeakingEvaluationResult> {
  return apiRequest<SpeakingEvaluationResult>('/placement/evaluate-speaking', 'POST', {
    question_id: questionId,
    user_transcript: userTranscript,
  })
}

export async function evaluateListening(
  questionId: number,
  userAnswer: string,
): Promise<ListeningEvaluationResult> {
  return apiRequest<ListeningEvaluationResult>('/placement/evaluate-listening', 'POST', {
    question_id: questionId,
    user_answer: userAnswer,
  })
}
