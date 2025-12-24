"use client"

import { Suspense, useCallback, useEffect, useState } from 'react'

import { AppShell } from '@/components/layout/app-shell'
import { ReviewQuiz } from '@/components/review/review-quiz'
import { SavedPhrasesList } from '@/components/review/saved-phrases-list'
import { fetchReviewStats } from '@/lib/saved-phrases'
import type { ReviewStats } from '@/types/review'

type TabType = 'today' | 'saved'

export default function ReviewPage(): JSX.Element {
  const [activeTab, setActiveTab] = useState<TabType>('today')
  const [stats, setStats] = useState<ReviewStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)

  const loadStats = useCallback(async () => {
    setStatsLoading(true)
    try {
      const data = await fetchReviewStats()
      setStats(data)
    } catch (err) {
      console.error('Failed to fetch review stats:', err)
    } finally {
      setStatsLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadStats()
  }, [loadStats])

  return (
    <AppShell>
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        {/* ヘッダー */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-blue-900">復習タイム</h1>
            <p className="mt-1 text-sm text-blue-600">
              改善フレーズを復習して、しっかり定着させましょう。
            </p>
          </div>

          {/* 完了率表示 */}
          {!statsLoading && stats && (
            <div className="flex items-center gap-3 rounded-xl border border-blue-200 bg-white/90 px-4 py-2 shadow-sm">
              <div className="text-center">
                <p className="text-xs font-medium uppercase tracking-wide text-blue-500">
                  累計完了率
                </p>
                <p className="text-lg font-bold text-blue-900">
                  {stats.completionRate.toFixed(0)}%
                </p>
              </div>
              <div className="h-10 w-10">
                <svg className="h-full w-full -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#e0e7ff"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray={`${stats.completionRate} 100`}
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <div className="text-xs text-blue-600">
                <p>{stats.completedItems} / {stats.totalItems}</p>
                <p>完了</p>
              </div>
            </div>
          )}
        </div>

        {/* タブ */}
        <div className="flex gap-1 rounded-lg bg-blue-100/50 p-1">
          <button
            type="button"
            onClick={() => setActiveTab('today')}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition ${
              activeTab === 'today'
                ? 'bg-white text-blue-900 shadow-sm'
                : 'text-blue-600 hover:text-blue-900'
            }`}
          >
            今日の復習
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('saved')}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition ${
              activeTab === 'saved'
                ? 'bg-white text-blue-900 shadow-sm'
                : 'text-blue-600 hover:text-blue-900'
            }`}
          >
            保存した表現
          </button>
        </div>

        {/* コンテンツ */}
        <Suspense fallback={<div className="p-4 text-blue-600">読み込み中…</div>}>
          {activeTab === 'today' ? <ReviewQuiz /> : <SavedPhrasesList />}
        </Suspense>
      </div>
    </AppShell>
  )
}

