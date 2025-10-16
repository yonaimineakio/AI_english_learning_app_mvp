"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

interface AuthGuardProps {
  children: React.ReactNode
  redirectTo?: string
  requireAuth?: boolean
}

export function AuthGuard({ 
  children, 
  redirectTo = '/login', 
  requireAuth = true 
}: AuthGuardProps): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isLoading) return // ローディング中は何もしない

    if (requireAuth && !isAuthenticated) {
      // 認証が必要だが未認証の場合
      router.push(redirectTo)
    } else if (!requireAuth && isAuthenticated) {
      // 認証が不要だが認証済みの場合（例：ログインページ）
      router.push('/')
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, router])

  // ローディング中は何も表示しない
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="text-sm text-blue-600">認証状態を確認中...</p>
        </div>
      </div>
    )
  }

  // 認証状態に応じて表示を制御
  if (requireAuth && !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-blue-600">認証が必要です</p>
        </div>
      </div>
    )
  }

  if (!requireAuth && isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-blue-600">リダイレクト中...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
