"use client"

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'

import { AppShell } from '@/components/layout/app-shell'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchSessionSummary, fetchReviewItems, startSession } from '@/lib/session'
import { SessionSummary } from '@/types/conversation'

export default function SummaryPage(): JSX.Element {
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('sessionId')

  // セッションサマリーの取得
  const { data: sessionSummary, isLoading: isSummaryLoading, error: summaryError } = useQuery({
    queryKey: ['sessionSummary', sessionId],
    queryFn: () => sessionId ? fetchSessionSummary(parseInt(sessionId)) : null,
    enabled: !!sessionId,
  })

  // 復習アイテムの取得
  const { data: reviewData, isLoading: isReviewLoading } = useQuery({
    queryKey: ['reviewItems'],
    queryFn: fetchReviewItems,
  })

  const isLoading = isSummaryLoading || isReviewLoading
  const hasError = summaryError

  if (isLoading) {
    return (
      <AppShell>
        <div className="mx-auto flex max-w-4xl flex-col gap-6">
          <div className="p-6 text-center text-blue-600">結果を読み込み中...</div>
        </div>
      </AppShell>
    )
  }

  if (hasError) {
    return (
      <AppShell>
        <div className="mx-auto flex max-w-4xl flex-col gap-6">
          <div className="p-6 text-center text-red-600">
            エラーが発生しました。ページを再読み込みしてください。
          </div>
        </div>
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <section className="flex flex-col gap-4 rounded-2xl border border-blue-100 bg-white/90 p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-blue-900">セッション結果</h1>
          {sessionSummary ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg text-blue-900">{sessionSummary.scenarioName || 'シナリオ'}</CardTitle>
                <CardDescription>
                  難易度: {sessionSummary.difficulty} / モード: {sessionSummary.mode}
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-2 text-sm text-blue-800">
                <span>完了ラウンド数: {sessionSummary.completedRounds}</span>
                <span>セッションID: {sessionSummary.sessionId}</span>
              </CardContent>
            </Card>
          ) : (
            <p className="text-sm text-blue-700">
              {sessionId ? 'セッション情報が取得できませんでした。' : 'セッションIDが指定されていません。'}
            </p>
          )}
        </section>

        <section className="grid gap-4 rounded-2xl border border-blue-100 bg-white/90 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-blue-900">改善トップ3フレーズ</h2>
          {sessionSummary?.topPhrases && sessionSummary.topPhrases.length > 0 ? (
            <div className="grid gap-3">
              {sessionSummary.topPhrases.map((phrase, index) => (
                <Card key={phrase.phrase}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base text-blue-900">#{index + 1}</CardTitle>
                    {phrase.roundIndex ? (
                      <CardDescription className="text-xs text-blue-500">Round {phrase.roundIndex}</CardDescription>
                    ) : null}
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-lg font-semibold text-blue-900">{phrase.phrase}</p>
                    <p className="text-sm text-blue-700">{phrase.explanation}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-sm text-blue-700">
              {sessionSummary ? '改善フレーズはまだ保存されていません。' : 'セッション情報を取得できませんでした。'}
            </p>
          )}
        </section>

        <section className="grid gap-4 rounded-2xl border border-blue-100 bg-white/90 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-blue-900">次回の復習</h2>
          <div className="space-y-3">
            <p className="text-sm text-blue-700">
              {sessionSummary?.nextReviewAt 
                ? `次回の復習は ${new Date(sessionSummary.nextReviewAt).toLocaleDateString('ja-JP')} に予定されています。`
                : '復習の予定はまだ設定されていません。'
              }
            </p>
            {reviewData && reviewData.totalCount > 0 && (
              <p className="text-sm text-blue-600">
                現在 {reviewData.totalCount} 件の復習アイテムがあります。
              </p>
            )}
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button className="sm:flex-1" onClick={() => void startSession({ scenarioId: 1, difficulty: 'intermediate', mode: 'standard', roundTarget: 6 })}>
              新しいセッションを開始する
            </Button>
            <Button asChild variant="outline" className="sm:flex-1">
              <Link href="/review">復習ページへ</Link>
            </Button>
          </div>
        </section>
      </div>
    </AppShell>
  )
}

