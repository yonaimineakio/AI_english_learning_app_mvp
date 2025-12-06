"use client"

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'

import { AuthGuard } from '@/components/auth/auth-guard'
import { AppShell } from '@/components/layout/app-shell'
import { Button } from '@/components/ui/button'
import { apiRequest } from '@/lib/api-client'

interface RankingEntry {
  rank: number
  user_id: number
  user_name: string
  total_points: number
}

interface RankingResponse {
  rankings: RankingEntry[]
  user_rank: number | null
}

function getMedalEmoji(rank: number): string {
  switch (rank) {
    case 1:
      return '🥇'
    case 2:
      return '🥈'
    case 3:
      return '🥉'
    default:
      return ''
  }
}

function getRankBgColor(rank: number): string {
  switch (rank) {
    case 1:
      return 'bg-gradient-to-r from-yellow-100 to-amber-100 border-yellow-300'
    case 2:
      return 'bg-gradient-to-r from-gray-100 to-slate-100 border-gray-300'
    case 3:
      return 'bg-gradient-to-r from-orange-100 to-amber-100 border-orange-300'
    default:
      return 'bg-white border-blue-100'
  }
}

export default function RankingPage(): JSX.Element {
  const { data: ranking, isLoading, error } = useQuery({
    queryKey: ['ranking'],
    queryFn: () => apiRequest<RankingResponse>('/users/ranking', 'GET'),
    staleTime: 60000, // Cache for 1 minute
  })

  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <div className="mx-auto max-w-3xl py-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-blue-900">ランキング</h1>
              <p className="mt-1 text-sm text-blue-600">
                ポイントに基づくユーザーランキング
              </p>
            </div>
            <Button asChild variant="outline">
              <Link href="/">← ホームに戻る</Link>
            </Button>
          </div>

          {isLoading && (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="animate-pulse rounded-xl border border-blue-100 bg-white p-4"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-8 w-8 rounded-full bg-blue-100" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-32 rounded bg-blue-100" />
                      <div className="h-3 w-20 rounded bg-blue-50" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              ランキングの読み込みに失敗しました。時間をおいて再度お試しください。
            </div>
          )}

          {ranking && (
            <div className="space-y-3">
              {/* User's rank if not in top */}
              {ranking.user_rank && ranking.user_rank > ranking.rankings.length && (
                <div className="mb-6 rounded-xl border-2 border-blue-500 bg-blue-50 p-4">
                  <p className="text-sm text-blue-700">
                    あなたの順位: <span className="font-bold text-lg">{ranking.user_rank}位</span>
                  </p>
                </div>
              )}

              {ranking.rankings.length === 0 ? (
                <div className="rounded-xl border border-blue-100 bg-white p-8 text-center">
                  <p className="text-blue-600">まだランキングデータがありません。</p>
                  <p className="mt-2 text-sm text-blue-500">
                    セッションを完了してポイントを獲得しましょう！
                  </p>
                </div>
              ) : (
                ranking.rankings.map((entry) => (
                  <div
                    key={entry.user_id}
                    className={`rounded-xl border p-4 shadow-sm transition-all hover:shadow-md ${getRankBgColor(
                      entry.rank
                    )}`}
                  >
                    <div className="flex items-center gap-4">
                      {/* Rank */}
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-lg font-bold text-blue-600 shadow-sm">
                        {getMedalEmoji(entry.rank) || entry.rank}
                      </div>

                      {/* User info */}
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{entry.user_name}</p>
                        <p className="text-sm text-gray-500">
                          {entry.total_points.toLocaleString()} ポイント
                        </p>
                      </div>

                      {/* Points badge */}
                      <div className="rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-purple-700">
                        ⭐ {entry.total_points.toLocaleString()} pt
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Point explanation */}
          <div className="mt-8 rounded-xl border border-blue-100 bg-blue-50/50 p-6">
            <h2 className="text-lg font-semibold text-blue-900 mb-4">ポイントの獲得方法</h2>
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="flex items-center gap-3 rounded-lg bg-white p-3 shadow-sm">
                <span className="text-2xl">📚</span>
                <div>
                  <p className="font-medium text-gray-900">セッション完了</p>
                  <p className="text-sm text-gray-500">+10 ポイント</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-lg bg-white p-3 shadow-sm">
                <span className="text-2xl">💬</span>
                <div>
                  <p className="font-medium text-gray-900">1ラウンドごと</p>
                  <p className="text-sm text-gray-500">+2 ポイント</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-lg bg-white p-3 shadow-sm">
                <span className="text-2xl">✅</span>
                <div>
                  <p className="font-medium text-gray-900">復習正解</p>
                  <p className="text-sm text-gray-500">+5 ポイント</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-lg bg-white p-3 shadow-sm">
                <span className="text-2xl">🔥</span>
                <div>
                  <p className="font-medium text-gray-900">連続学習ボーナス</p>
                  <p className="text-sm text-gray-500">+5 ポイント/日</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </AppShell>
    </AuthGuard>
  )
}
