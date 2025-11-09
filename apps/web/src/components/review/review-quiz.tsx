"use client"

import { useCallback, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { completeReviewItem, fetchReviewItems } from '@/lib/session'
import type { ReviewItem, ReviewResult } from '@/types/review'

interface QuizState {
  items: ReviewItem[]
  activeIndex: number
  totalCount: number
}

const REVIEW_OPTIONS: ReviewResult[] = ['correct', 'incorrect']

export function ReviewQuiz(): JSX.Element {
  const [state, setState] = useState<QuizState>({ items: [], activeIndex: 0, totalCount: 0 })
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const activeItem = useMemo(() => state.items[state.activeIndex] ?? null, [state])

  const loadReviews = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetchReviewItems()
      setState({ items: response.reviewItems, activeIndex: 0, totalCount: response.totalCount })
    } catch (err) {
      setError(err instanceof Error ? err.message : '復習アイテムの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadReviews()
  }, [loadReviews])

  const handleSubmit = useCallback(
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

  if (!activeItem) {
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
      </CardHeader>
      <CardContent className="space-y-6">
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
              onClick={() => void handleSubmit(option)}
              disabled={submitting}
            >
              {option === 'correct' ? '覚えた！' : 'もう一度'}
            </Button>
          ))}
        </div>

        <Button variant="ghost" size="sm" onClick={() => void loadReviews()} disabled={submitting}>
          リストを再読み込み
        </Button>
      </CardContent>
    </Card>
  )
}


