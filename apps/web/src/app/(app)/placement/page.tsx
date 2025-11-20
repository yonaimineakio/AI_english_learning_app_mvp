"use client"

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQuery } from '@tanstack/react-query'

import { AuthGuard } from '@/components/auth/auth-guard'
import { AppShell } from '@/components/layout/app-shell'
import {
  PlacementQuestion,
  fetchPlacementQuestions,
  submitPlacementAnswers,
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

export default function PlacementPage(): JSX.Element {
  const router = useRouter()
  const [scores, setScores] = useState<Record<number, number>>({})
  const [playingQuestionId, setPlayingQuestionId] = useState<number | null>(null)
  const [ttsError, setTtsError] = useState<string | null>(null)

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
    mutationFn: () =>
      submitPlacementAnswers(
        (questions ?? []).map((q) => ({
          question_id: q.id,
          self_score: scores[q.id] ?? 0,
        })),
      ),
    onSuccess: () => {
      router.push('/')
    },
  })

  useEffect(() => {
    if (!isUserLoading && user && user.placement_completed_at) {
      router.replace('/')
    }
  }, [isUserLoading, user, router])

  const handleScoreChange = (questionId: number, value: number) => {
    setScores((prev) => ({ ...prev, [questionId]: value }))
  }

  const handlePlayQuestion = async (question: PlacementQuestion) => {
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
  }

  const handleSubmit = () => {
    if (!questions || submitMutation.isPending) return
    submitMutation.mutate()
  }

  const isLoading = isUserLoading || isQuestionsLoading

  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <div className="mx-auto max-w-3xl py-6">
          <h1 className="text-2xl font-semibold text-blue-900">レベル判定テスト</h1>
          <p className="mt-2 text-sm text-blue-700">
            リスニングとスピーキングに関する20問に自己評価で回答し、現在のレベルを判定します。
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

          {!isLoading && questions && (
            <div className="mt-6 space-y-4">
              {questions.map((q: PlacementQuestion) => (
                <div
                  key={q.id}
                  className="rounded-2xl border border-blue-100 bg-white/95 p-4 shadow-sm"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                        {q.type === 'listening' ? 'Listening' : 'Speaking'}
                      </span>
                      {q.type === 'listening' && (
                        <button
                          type="button"
                          onClick={() => handlePlayQuestion(q)}
                          disabled={playingQuestionId !== null}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-xs text-blue-700 shadow-sm hover:border-blue-400 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
                          aria-label="問題文を音声で再生"
                        >
                          {playingQuestionId === q.id ? '…' : '🔊'}
                        </button>
                      )}
                    </div>
                    {q.scenario_hint ? (
                      <span className="text-xs text-blue-500">{q.scenario_hint}</span>
                    ) : null}
                  </div>
                  <p className="mt-2 text-sm text-blue-900">{q.prompt}</p>

                  <div className="mt-3 space-y-1 text-xs text-blue-700">
                    <p>自己評価（0〜5）: 自信の度合いを選んでください。</p>
                    <div className="flex items-center gap-2">
                      {[0, 1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          type="button"
                          onClick={() => handleScoreChange(q.id, value)}
                          className={`flex h-8 w-8 items-center justify-center rounded-full border text-xs font-semibold transition ${
                            (scores[q.id] ?? 0) === value
                              ? 'border-blue-500 bg-blue-500 text-white'
                              : 'border-blue-200 bg-white text-blue-700 hover:border-blue-400'
                          }`}
                        >
                          {value}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}

              <div className="mt-6 flex justify-end">
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={submitMutation.isPending}
                  className="rounded-lg bg-blue-600 px-6 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                >
                  {submitMutation.isPending ? '判定中…' : 'レベルを判定してシナリオ選択へ進む'}
                </button>
              </div>

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


