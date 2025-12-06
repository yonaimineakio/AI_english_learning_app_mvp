"use client"

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api-client'

interface StreakInfo {
  current_streak: number
  longest_streak: number
  last_activity_date: string | null
  is_active_today: boolean
}

interface UserStats {
  total_sessions: number
  total_rounds: number
  total_points: number
  streak: StreakInfo
}

export function StreakDisplay() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => apiRequest<UserStats>('/users/stats', 'GET'),
    staleTime: 60000, // Cache for 1 minute
  })

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-blue-100 bg-white/80 p-4 animate-pulse">
        <div className="h-4 w-24 bg-blue-100 rounded mb-2" />
        <div className="h-8 w-16 bg-blue-100 rounded" />
      </div>
    )
  }

  if (error || !stats) {
    return null
  }

  const { streak, total_sessions, total_rounds, total_points } = stats

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {/* Streak card */}
      <div className="rounded-2xl border border-orange-200 bg-gradient-to-br from-orange-50 to-yellow-50 p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">🔥</span>
          <span className="text-sm font-medium text-orange-700">連続学習</span>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-orange-600">{streak.current_streak}</span>
          <span className="text-sm text-orange-500">日</span>
        </div>
        {streak.longest_streak > 0 && (
          <p className="mt-1 text-xs text-orange-500">
            最長記録: {streak.longest_streak}日
          </p>
        )}
        {streak.is_active_today && (
          <div className="mt-2 flex items-center gap-1 text-xs text-green-600">
            <span className="inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            今日も学習済み！
          </div>
        )}
      </div>

      {/* Sessions card */}
      <div className="rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-indigo-50 p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">📚</span>
          <span className="text-sm font-medium text-blue-700">セッション数</span>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-blue-600">{total_sessions}</span>
          <span className="text-sm text-blue-500">回</span>
        </div>
      </div>

      {/* Rounds card */}
      <div className="rounded-2xl border border-green-100 bg-gradient-to-br from-green-50 to-emerald-50 p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">💬</span>
          <span className="text-sm font-medium text-green-700">会話ラウンド</span>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-green-600">{total_rounds}</span>
          <span className="text-sm text-green-500">回</span>
        </div>
      </div>

      {/* Points card */}
      <Link
        href="/ranking"
        className="rounded-2xl border border-purple-100 bg-gradient-to-br from-purple-50 to-pink-50 p-4 shadow-sm transition-all hover:shadow-md hover:border-purple-200 block"
      >
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl">⭐</span>
          <span className="text-sm font-medium text-purple-700">ポイント</span>
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-purple-600">{total_points}</span>
          <span className="text-sm text-purple-500">pt</span>
        </div>
        <p className="mt-1 text-xs text-purple-400 hover:text-purple-600">
          ランキングを見る →
        </p>
      </Link>
    </div>
  )
}
