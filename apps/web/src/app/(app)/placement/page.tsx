"use client"

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQuery } from '@tanstack/react-query'

import { AuthGuard } from '@/components/auth/auth-guard'
import { AppShell } from '@/components/layout/app-shell'
import { AudioRecorder } from '@/components/audio/audio-recorder'
import { WordMatchDisplay } from '@/components/placement/word-match-display'
import { WordPuzzle } from '@/components/placement/word-puzzle'
import { Button } from '@/components/ui/button'
import {
  PlacementQuestion,
  fetchPlacementQuestions,
  submitPlacementAnswers,
  evaluateSpeaking,
  evaluateListening,
  SpeakingEvaluationResult,
  ListeningEvaluationResult,
  PlacementAnswerPayload,
} from '@/lib/placement'
import { apiRequest } from '@/lib/api-client'
import { playTextWithTts } from '@/lib/tts'

interface CurrentUser {
  id: number
  name: string
  email: string
  placement_level?: 'beginner' | 'intermediate' | 'advanced'
  placement_completed_at?: string | null
}

interface QuestionResult {
  questionId: number
  type: 'speaking' | 'listening'
  speakingResult?: SpeakingEvaluationResult
  listeningResult?: ListeningEvaluationResult
}

export default function PlacementPage(): JSX.Element {
  const router = useRouter()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [results, setResults] = useState<Map<number, QuestionResult>>(new Map())
  const [playingQuestionId, setPlayingQuestionId] = useState<number | null>(null)
  const [ttsError, setTtsError] = useState<string | null>(null)
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [showResult, setShowResult] = useState(false)

  const { data: user, isLoading: isUserLoading } = useQuery({
    queryKey: ['current-user'],
    queryFn: () => apiRequest<CurrentUser>('/auth/me', 'GET'),
  })

  const {
    data: questions,
    isLoading: isQuestionsLoading,
    error: questionsError,
  } = useQuery({
    queryKey: ['placement-questions'],
    queryFn: fetchPlacementQuestions,
    enabled: !!user && !user.placement_completed_at,
  })

  const submitMutation = useMutation({
    mutationFn: (answers: PlacementAnswerPayload[]) => submitPlacementAnswers(answers),
    onSuccess: () => {
      router.push('/')
    },
  })

  useEffect(() => {
    if (!isUserLoading && user && user.placement_completed_at) {
      router.replace('/')
    }
  }, [isUserLoading, user, router])

  const currentQuestion = useMemo(() => {
    if (!questions || questions.length === 0) return null
    return questions[currentIndex] ?? null
  }, [questions, currentIndex])

  const currentResult = useMemo(() => {
    if (!currentQuestion) return null
    return results.get(currentQuestion.id) ?? null
  }, [currentQuestion, results])

  const progress = useMemo(() => {
    if (!questions || questions.length === 0) return 0
    return ((currentIndex + 1) / questions.length) * 100
  }, [currentIndex, questions])

  const handlePlayQuestion = useCallback(async (question: PlacementQuestion) => {
    if (playingQuestionId !== null) return
    try {
      setTtsError(null)
      setPlayingQuestionId(question.id)
      await playTextWithTts(
        question.prompt,
        question.type === 'listening' ? 'placement_listening' : undefined,
      )
    } catch (error) {
      console.error('Failed to play TTS for question', question.id, error)
      setTtsError('音声の再生に失敗しました')
    } finally {
      setPlayingQuestionId(null)
    }
  }, [playingQuestionId])

  // Speaking evaluation handler
  const handleSpeakingTranscription = useCallback(async (transcript: string) => {
    if (!currentQuestion || currentQuestion.type !== 'speaking') return

    setIsEvaluating(true)
    try {
      const result = await evaluateSpeaking(currentQuestion.id, transcript)
      setResults((prev) => {
        const next = new Map(prev)
        next.set(currentQuestion.id, {
          questionId: currentQuestion.id,
          type: 'speaking',
          speakingResult: result,
        })
        return next
      })
      setShowResult(true)
    } catch (error) {
      console.error('Speaking evaluation error:', error)
      setTtsError('評価に失敗しました。もう一度お試しください。')
    } finally {
      setIsEvaluating(false)
    }
  }, [currentQuestion])

  // Listening evaluation handler
  const handleListeningSubmit = useCallback(async (answer: string) => {
    if (!currentQuestion || currentQuestion.type !== 'listening') return

    setIsEvaluating(true)
    try {
      const result = await evaluateListening(currentQuestion.id, answer)
      setResults((prev) => {
        const next = new Map(prev)
        next.set(currentQuestion.id, {
          questionId: currentQuestion.id,
          type: 'listening',
          listeningResult: result,
        })
        return next
      })
      setShowResult(true)
    } catch (error) {
      console.error('Listening evaluation error:', error)
      setTtsError('評価に失敗しました。もう一度お試しください。')
    } finally {
      setIsEvaluating(false)
    }
  }, [currentQuestion])

  const handleNext = useCallback(() => {
    if (!questions) return

    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1)
      setShowResult(false)
    }
  }, [currentIndex, questions])

  const handlePrev = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1)
      setShowResult(false)
    }
  }, [currentIndex])

  const handleSubmit = useCallback(() => {
    if (!questions || submitMutation.isPending) return

    // Convert results to answer payloads
    const answers: PlacementAnswerPayload[] = questions.map((q) => {
      const result = results.get(q.id)
      if (result?.type === 'speaking' && result.speakingResult) {
        return {
          question_id: q.id,
          speaking_score: result.speakingResult.score,
        }
      } else if (result?.type === 'listening' && result.listeningResult) {
        return {
          question_id: q.id,
          listening_correct: result.listeningResult.correct,
        }
      } else {
        // Default to 0 if not answered
        return {
          question_id: q.id,
          self_score: 0,
        }
      }
    })

    submitMutation.mutate(answers)
  }, [questions, results, submitMutation])

  const answeredCount = useMemo(() => {
    return results.size
  }, [results])

  const canSubmit = useMemo(() => {
    if (!questions) return false
    // Allow submission if at least half the questions are answered
    return answeredCount >= Math.floor(questions.length / 2)
  }, [questions, answeredCount])

  const isLoading = isUserLoading || isQuestionsLoading

  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <div className="mx-auto max-w-3xl py-6">
          <h1 className="text-2xl font-semibold text-blue-900">レベル判定テスト</h1>
          <p className="mt-2 text-sm text-blue-700">
            リスニングとスピーキングの20問に回答し、現在のレベルを判定します。
          </p>

          {isLoading && (
            <div className="mt-8 rounded-2xl border border-blue-100 bg-white/80 p-4 text-sm text-blue-700">
              読み込み中です…
            </div>
          )}

          {questionsError ? (
            <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              テストの読み込みに失敗しました。時間をおいて再度お試しください。
            </div>
          ) : null}

          {!isLoading && questions && currentQuestion && (
            <div className="mt-6 space-y-4">
              {/* Progress bar */}
              <div className="mb-6">
                <div className="flex items-center justify-between text-xs text-blue-600 mb-2">
                  <span>問題 {currentIndex + 1} / {questions.length}</span>
                  <span>回答済み: {answeredCount} / {questions.length}</span>
                </div>
                <div className="h-2 w-full rounded-full bg-blue-100">
                  <div
                    className="h-2 rounded-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Question card */}
              <div className="rounded-2xl border border-blue-100 bg-white/95 p-5 shadow-sm">
                <div className="flex items-center justify-between gap-3 mb-4">
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                      currentQuestion.type === 'listening'
                        ? 'bg-purple-50 text-purple-700'
                        : 'bg-green-50 text-green-700'
                    }`}>
                      {currentQuestion.type === 'listening' ? '🎧 Listening' : '🎤 Speaking'}
                    </span>
                    {currentQuestion.type === 'listening' && (
                      <button
                        type="button"
                        onClick={() => handlePlayQuestion(currentQuestion)}
                        disabled={playingQuestionId !== null}
                        className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-purple-200 bg-purple-50 text-xs text-purple-700 shadow-sm hover:border-purple-400 hover:bg-purple-100 disabled:cursor-not-allowed disabled:opacity-50"
                        aria-label="問題文を音声で再生"
                      >
                        {playingQuestionId === currentQuestion.id ? '…' : '🔊'}
                      </button>
                    )}
                  </div>
                  {currentQuestion.scenario_hint ? (
                    <span className="text-xs text-blue-500">{currentQuestion.scenario_hint}</span>
                  ) : null}
                </div>

                {/* Speaking question UI */}
                {currentQuestion.type === 'speaking' && (
                  <div className="space-y-4">
                    <div className="rounded-lg bg-green-50 border border-green-200 p-4">
                      <p className="text-xs text-green-600 mb-1">この文を読んでください:</p>
                      <p className="text-lg font-medium text-green-900">{currentQuestion.prompt}</p>
                    </div>

                    {!showResult && (
                      <div className="pt-2">
                        <AudioRecorder
                          onTranscriptionComplete={handleSpeakingTranscription}
                          onError={(error) => setTtsError(error)}
                          disabled={isEvaluating}
                        />
                        {isEvaluating && (
                          <div className="mt-2 flex items-center gap-2 text-sm text-blue-600">
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
                            評価中...
                          </div>
                        )}
                      </div>
                    )}

                    {showResult && currentResult?.speakingResult && (
                      <div className="space-y-4">
                        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                          <p className="text-xs text-blue-600 mb-2">評価結果:</p>
                          <WordMatchDisplay
                            wordMatches={currentResult.speakingResult.word_matches}
                            score={currentResult.speakingResult.score}
                            matchedCount={currentResult.speakingResult.matched_count}
                            totalCount={currentResult.speakingResult.total_count}
                          />
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowResult(false)}
                        >
                          もう一度録音する
                        </Button>
                      </div>
                    )}
                  </div>
                )}

                {/* Listening question UI */}
                {currentQuestion.type === 'listening' && (
                  <div className="space-y-4">
                    <div className="rounded-lg bg-purple-50 border border-purple-200 p-4">
                      <p className="text-xs text-purple-600 mb-1">音声を聞いて、単語を並び替えてください:</p>
                      <button
                        type="button"
                        onClick={() => handlePlayQuestion(currentQuestion)}
                        disabled={playingQuestionId !== null}
                        className="flex items-center gap-2 mt-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-700 font-medium hover:bg-purple-200 disabled:opacity-50"
                      >
                        {playingQuestionId === currentQuestion.id ? (
                          <>
                            <span className="h-2 w-2 rounded-full bg-purple-500 animate-pulse" />
                            再生中...
                          </>
                        ) : (
                          <>🔊 音声を再生</>
                        )}
                      </button>
                    </div>

                    {!showResult && currentQuestion.word_options && (
                      <WordPuzzle
                        wordOptions={currentQuestion.word_options}
                        distractorWords={currentQuestion.distractor_words || []}
                        onSubmit={handleListeningSubmit}
                        disabled={isEvaluating}
                      />
                    )}

                    {isEvaluating && (
                      <div className="flex items-center gap-2 text-sm text-blue-600">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
                        評価中...
                      </div>
                    )}

                    {showResult && currentResult?.listeningResult && (
                      <div className="space-y-4">
                        <div className={`rounded-lg border p-4 ${
                          currentResult.listeningResult.correct
                            ? 'bg-green-50 border-green-200'
                            : 'bg-red-50 border-red-200'
                        }`}>
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-2xl ${
                              currentResult.listeningResult.correct ? '' : ''
                            }`}>
                              {currentResult.listeningResult.correct ? '✅' : '❌'}
                            </span>
                            <p className={`text-sm font-medium ${
                              currentResult.listeningResult.correct
                                ? 'text-green-700'
                                : 'text-red-700'
                            }`}>
                              {currentResult.listeningResult.correct ? '正解！' : '不正解'}
                            </p>
                          </div>
                          {!currentResult.listeningResult.correct && (
                            <p className="text-sm text-gray-600">
                              正解: <span className="font-medium">{currentResult.listeningResult.expected}</span>
                            </p>
                          )}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowResult(false)}
                        >
                          もう一度挑戦する
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Navigation buttons */}
              <div className="flex items-center justify-between pt-4">
                <Button
                  variant="outline"
                  onClick={handlePrev}
                  disabled={currentIndex === 0}
                >
                  ← 前の問題
                </Button>

                <div className="flex gap-2">
                  {currentIndex < questions.length - 1 ? (
                    <Button onClick={handleNext}>
                      次の問題 →
                    </Button>
                  ) : (
                    <Button
                      onClick={handleSubmit}
                      disabled={!canSubmit || submitMutation.isPending}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      {submitMutation.isPending ? '判定中…' : 'レベルを判定する'}
                    </Button>
                  )}
                </div>
              </div>

              {/* Skip to submit button */}
              {canSubmit && currentIndex < questions.length - 1 && (
                <div className="text-center pt-2">
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={submitMutation.isPending}
                    className="text-sm text-blue-600 hover:text-blue-800 underline"
                  >
                    回答を終了してレベルを判定する（{answeredCount}問回答済み）
                  </button>
                </div>
              )}

              {ttsError ? (
                <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
                  {ttsError}
                </div>
              ) : null}
            </div>
          )}
        </div>
      </AppShell>
    </AuthGuard>
  )
}
