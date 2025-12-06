"use client"

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AudioRecorder } from '@/components/audio/audio-recorder'
import { WordMatchDisplay } from '@/components/placement/word-match-display'
import { WordPuzzle } from '@/components/placement/word-puzzle'
import {
  fetchReviewItems,
  fetchNextReviewProblem,
  evaluateReviewProblem,
  completeReviewItem,
} from '@/lib/session'
import { playTextWithTts } from '@/lib/tts'
import type { ReviewItem, ReviewResult, ReviewProblem, ReviewEvaluationResult } from '@/types/review'

type ReviewMode = 'phrase' | 'problem'

interface QuizState {
  items: ReviewItem[]
  activeIndex: number
  totalCount: number
}

const REVIEW_OPTIONS: ReviewResult[] = ['correct', 'incorrect']

export function ReviewQuiz(): JSX.Element {
  const [mode, setMode] = useState<ReviewMode>('problem')
  const [state, setState] = useState<QuizState>({ items: [], activeIndex: 0, totalCount: 0 })
  const [problem, setProblem] = useState<ReviewProblem | null>(null)
  const [evaluationResult, setEvaluationResult] = useState<ReviewEvaluationResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isPlayingTts, setIsPlayingTts] = useState(false)

  const activeItem = state.items[state.activeIndex] ?? null

  // Load review items
  const loadReviews = useCallback(async () => {
    setLoading(true)
    setError(null)
    setEvaluationResult(null)
    try {
      const response = await fetchReviewItems()
      setState({ items: response.reviewItems, activeIndex: 0, totalCount: response.totalCount })

      // Try to load a problem if in problem mode
      if (mode === 'problem' && response.reviewItems.length > 0) {
        try {
          const prob = await fetchNextReviewProblem()
          setProblem(prob)
        } catch {
          // Fall back to phrase mode if problem API fails
          setMode('phrase')
          setProblem(null)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '復習アイテムの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }, [mode])

  // Load next problem
  const loadNextProblem = useCallback(async () => {
    setSubmitting(true)
    setError(null)
    setEvaluationResult(null)
    try {
      const prob = await fetchNextReviewProblem()
      setProblem(prob)
    } catch (err) {
      // No more problems or error
      setProblem(null)
      await loadReviews()
    } finally {
      setSubmitting(false)
    }
  }, [loadReviews])

  useEffect(() => {
    void loadReviews()
  }, [loadReviews])

  // Handle phrase mode submit
  const handlePhraseSubmit = useCallback(
    async (result: ReviewResult) => {
      if (!activeItem) return

      setSubmitting(true)
      setError(null)
      setSuccessMessage(null)

      try {
        const updated = await completeReviewItem(activeItem.id, result)

        setSuccessMessage(result === 'correct' ? 'よくできました！' : 'もう一度復習しましょう。')

        setState((prev) => {
          const nextItems = [...prev.items]
          nextItems[prev.activeIndex] = { ...updated }

          const remaining = nextItems.filter((item) => !item.isCompleted)

          if (remaining.length === 0) {
            return { items: [], activeIndex: 0, totalCount: prev.totalCount }
          }

          const nextActive = nextItems.findIndex((item) => !item.isCompleted)

          return {
            items: nextItems,
            activeIndex: nextActive === -1 ? 0 : nextActive,
            totalCount: prev.totalCount,
          }
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : '復習結果の送信に失敗しました')
      } finally {
        setSubmitting(false)
      }
    },
    [activeItem],
  )

  // Handle speaking transcription
  const handleSpeakingTranscription = useCallback(
    async (transcript: string) => {
      if (!problem || problem.type !== 'speaking') return

      setSubmitting(true)
      setError(null)
      try {
        const result = await evaluateReviewProblem(
          problem.review_item_id,
          'speaking',
          transcript,
        )
        setEvaluationResult(result)
        setSuccessMessage(result.is_correct ? 'よくできました！' : 'もう一度練習しましょう。')
      } catch (err) {
        setError(err instanceof Error ? err.message : '評価に失敗しました')
      } finally {
        setSubmitting(false)
      }
    },
    [problem],
  )

  // Handle listening submit
  const handleListeningSubmit = useCallback(
    async (answer: string) => {
      if (!problem || problem.type !== 'listening') return

      setSubmitting(true)
      setError(null)
      try {
        const result = await evaluateReviewProblem(
          problem.review_item_id,
          'listening',
          answer,
        )
        setEvaluationResult(result)
        setSuccessMessage(result.is_correct ? '正解！' : '不正解')
      } catch (err) {
        setError(err instanceof Error ? err.message : '評価に失敗しました')
      } finally {
        setSubmitting(false)
      }
    },
    [problem],
  )

  // Handle TTS playback
  const handlePlayTts = useCallback(async (text: string) => {
    if (isPlayingTts) return
    setIsPlayingTts(true)
    try {
      await playTextWithTts(text)
    } catch (err) {
      console.error('TTS error:', err)
    } finally {
      setIsPlayingTts(false)
    }
  }, [isPlayingTts])

  // Switch mode
  const handleModeSwitch = useCallback((newMode: ReviewMode) => {
    setMode(newMode)
    setEvaluationResult(null)
    setProblem(null)
    setSuccessMessage(null)
  }, [])

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>復習アイテムを読み込み中...</CardTitle>
          <CardDescription className="text-blue-600">少々お待ちください。</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>復習アイテムの取得に失敗しました</CardTitle>
          <CardDescription className="text-red-600">{error}</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button onClick={() => void loadReviews()}>再読み込み</Button>
          <Button asChild variant="outline">
            <Link href="/">セッションに戻る</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  if (!activeItem && !problem) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>復習が完了しています</CardTitle>
          <CardDescription className="text-blue-600">また明日、復習を続けましょう！</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-3">
          <Button variant="outline" onClick={() => void loadReviews()}>
            更新する
          </Button>
          <Button asChild>
            <Link href="/">セッションに戻る</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  const remainingCount = state.items.filter((item) => !item.isCompleted).length

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>今日の復習</CardTitle>
        <CardDescription className="text-blue-600">
          残り {remainingCount} 件 / 全 {state.totalCount} 件
        </CardDescription>
        {/* Mode switch */}
        <div className="flex gap-2 mt-2">
          <button
            type="button"
            onClick={() => handleModeSwitch('problem')}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              mode === 'problem'
                ? 'bg-blue-600 text-white'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            🎯 問題形式
          </button>
          <button
            type="button"
            onClick={() => handleModeSwitch('phrase')}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              mode === 'phrase'
                ? 'bg-blue-600 text-white'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            📝 フレーズ確認
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Problem mode */}
        {mode === 'problem' && problem && (
          <div className="space-y-4">
            {/* Problem type badge */}
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
                problem.type === 'speaking'
                  ? 'bg-green-50 text-green-700'
                  : problem.type === 'listening'
                  ? 'bg-purple-50 text-purple-700'
                  : 'bg-blue-50 text-blue-700'
              }`}>
                {problem.type === 'speaking' ? '🎤 Speaking' : problem.type === 'listening' ? '🎧 Listening' : '📝 Phrase'}
              </span>
            </div>

            {/* Target phrase */}
            <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-4">
              <p className="text-xs uppercase text-blue-500">復習フレーズ</p>
              <p className="mt-2 text-lg font-semibold text-blue-900">{problem.phrase}</p>
              <p className="mt-1 text-sm text-blue-700">{problem.explanation}</p>
            </div>

            {/* Speaking problem */}
            {problem.type === 'speaking' && problem.sentence && (
              <div className="space-y-4">
                <div className="rounded-lg bg-green-50 border border-green-200 p-4">
                  <p className="text-xs text-green-600 mb-1">この文を読んでください:</p>
                  <p className="text-lg font-medium text-green-900">{problem.sentence}</p>
                </div>

                {!evaluationResult && (
                  <AudioRecorder
                    onTranscriptionComplete={handleSpeakingTranscription}
                    onError={(err) => setError(err)}
                    disabled={submitting}
                  />
                )}

                {evaluationResult?.speaking_result && (
                  <div className="space-y-4">
                    <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
                      <p className="text-xs text-blue-600 mb-2">評価結果:</p>
                      <WordMatchDisplay
                        wordMatches={evaluationResult.speaking_result.word_matches}
                        score={evaluationResult.speaking_result.score}
                        matchedCount={evaluationResult.speaking_result.matched_count}
                        totalCount={evaluationResult.speaking_result.total_count}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Listening problem */}
            {problem.type === 'listening' && problem.sentence && problem.word_options && (
              <div className="space-y-4">
                <div className="rounded-lg bg-purple-50 border border-purple-200 p-4">
                  <p className="text-xs text-purple-600 mb-1">音声を聞いて、単語を並び替えてください:</p>
                  <button
                    type="button"
                    onClick={() => handlePlayTts(problem.sentence!)}
                    disabled={isPlayingTts}
                    className="flex items-center gap-2 mt-2 px-4 py-2 rounded-lg bg-purple-100 text-purple-700 font-medium hover:bg-purple-200 disabled:opacity-50"
                  >
                    {isPlayingTts ? (
                      <>
                        <span className="h-2 w-2 rounded-full bg-purple-500 animate-pulse" />
                        再生中...
                      </>
                    ) : (
                      <>🔊 音声を再生</>
                    )}
                  </button>
                </div>

                {!evaluationResult && (
                  <WordPuzzle
                    wordOptions={problem.word_options}
                    distractorWords={problem.distractors || []}
                    onSubmit={handleListeningSubmit}
                    disabled={submitting}
                  />
                )}

                {evaluationResult && (
                  <div className={`rounded-lg border p-4 ${
                    evaluationResult.is_correct
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">
                        {evaluationResult.is_correct ? '✅' : '❌'}
                      </span>
                      <p className={`text-sm font-medium ${
                        evaluationResult.is_correct ? 'text-green-700' : 'text-red-700'
                      }`}>
                        {evaluationResult.is_correct ? '正解！' : '不正解'}
                      </p>
                    </div>
                    {!evaluationResult.is_correct && evaluationResult.expected && (
                      <p className="text-sm text-gray-600">
                        正解: <span className="font-medium">{evaluationResult.expected}</span>
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Success/error messages */}
            {successMessage && (
              <p className={`text-sm ${evaluationResult?.is_correct ? 'text-green-600' : 'text-orange-600'}`}>
                {successMessage}
              </p>
            )}

            {/* Next/retry buttons */}
            {evaluationResult && (
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setEvaluationResult(null)
                    setSuccessMessage(null)
                  }}
                >
                  もう一度
                </Button>
                <Button onClick={() => void loadNextProblem()}>
                  次の問題へ
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Phrase mode */}
        {mode === 'phrase' && activeItem && (
          <>
            <div className="rounded-lg border border-blue-100 bg-white/70 p-4">
              <p className="text-xs uppercase text-blue-500">改善フレーズ</p>
              <p className="mt-2 text-lg font-semibold text-blue-900">{activeItem.phrase}</p>
            </div>

            <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-4">
              <p className="text-xs uppercase text-blue-500">フィードバック</p>
              <p className="mt-2 text-sm text-blue-900">{activeItem.explanation}</p>
            </div>

            {successMessage && <p className="text-sm text-green-600">{successMessage}</p>}

            <div className="flex flex-col gap-3 sm:flex-row">
              {REVIEW_OPTIONS.map((option) => (
                <Button
                  key={option}
                  variant={option === 'correct' ? 'primary' : 'outline'}
                  className="flex-1"
                  onClick={() => void handlePhraseSubmit(option)}
                  disabled={submitting}
                >
                  {option === 'correct' ? '覚えた！' : 'もう一度'}
                </Button>
              ))}
            </div>
          </>
        )}

        <Button variant="ghost" size="sm" onClick={() => void loadReviews()} disabled={submitting}>
          リストを再読み込み
        </Button>
      </CardContent>
    </Card>
  )
}
