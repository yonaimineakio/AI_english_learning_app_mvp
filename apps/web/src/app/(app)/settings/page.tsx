"use client"

import { useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'

import { AppShell } from '@/components/layout/app-shell'
import { AuthGuard } from '@/components/auth/auth-guard'
import { Button } from '@/components/ui/button'
import { apiRequest } from '@/lib/api-client'

interface CurrentUser {
  id: number
  name: string
  email: string
  placement_level?: 'beginner' | 'intermediate' | 'advanced'
  placement_score?: number | null
  placement_completed_at?: string | null
}

function formatLevel(level?: CurrentUser['placement_level']): string {
  if (!level) return '未判定'
  switch (level) {
    case 'beginner':
      return '初級 (beginner)'
    case 'intermediate':
      return '中級 (intermediate)'
    case 'advanced':
      return '上級 (advanced)'
    default:
      return level
  }
}

function formatDateTime(value?: string | null): string {
  if (!value) return '未受験'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '未受験'
  return date.toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
}

export default function SettingsPage(): JSX.Element {
  const router = useRouter()

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['current-user-settings'],
    queryFn: () => apiRequest<CurrentUser>('/auth/me', 'GET'),
  })

  const initialLetter = useMemo(() => {
    if (!user) return '?'
    const base = user.name || user.email
    return base?.trim()?.charAt(0)?.toUpperCase() ?? '?'
  }, [user])

  const handleRetakePlacement = () => {
    router.push('/placement')
  }

  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <div className="mx-auto max-w-3xl space-y-6">
          <header className="border-b border-blue-100 pb-4">
            <h1 className="text-xl font-semibold text-blue-900">ユーザー設定</h1>
            <p className="mt-1 text-xs text-blue-600">
              プロフィール情報と現在のレベルを確認し、必要に応じてレベル判定テストを受け直すことができます。
            </p>
          </header>

          <section className="grid gap-4 md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
            <div className="rounded-2xl border border-blue-100 bg-white/95 p-4 shadow-sm">
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white shadow">
                  {initialLetter}
                </div>
                <div>
                  <p className="text-sm font-semibold text-blue-900">
                    {isLoading ? '読み込み中…' : user?.name ?? '---'}
                  </p>
                  <p className="mt-1 text-xs text-blue-600">{user?.email ?? ''}</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-blue-100 bg-white/95 p-4 shadow-sm">
              <h2 className="text-sm font-semibold text-blue-900">現在のレベル</h2>
              <dl className="mt-3 space-y-2 text-sm text-blue-800">
                <div className="flex items-center justify-between">
                  <dt className="text-xs text-blue-500">レベル</dt>
                  <dd className="font-semibold">{formatLevel(user?.placement_level)}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-xs text-blue-500">スコア</dt>
                  <dd>{user?.placement_score ?? '—'}</dd>
                </div>
                <div className="flex items-center justify-between">
                  <dt className="text-xs text-blue-500">最終レベル判定日</dt>
                  <dd className="text-right text-xs">{formatDateTime(user?.placement_completed_at)}</dd>
                </div>
              </dl>

              <div className="mt-4">
                <Button
                  type="button"
                  className="w-full"
                  variant="outline"
                  onClick={handleRetakePlacement}
                  disabled={isLoading}
                >
                  レベル判定テストを受け直す
                </Button>
                <p className="mt-2 text-xs text-blue-600">
                  レベルを確認し直したい場合は、レベル判定テストを再度受けることができます。
                </p>
              </div>
            </div>
          </section>

          {error ? (
            <p className="text-xs text-red-600">
              ユーザー情報の取得に失敗しました。ページを再読み込みしてもう一度お試しください。
            </p>
          ) : null}
        </div>
      </AppShell>
    </AuthGuard>
  )
}


