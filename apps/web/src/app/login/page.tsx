"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { AuthGuard } from '@/components/auth/auth-guard'
import { LoginButton } from '@/components/auth/login-button'
import { AppShell } from '@/components/layout/app-shell'

export default function LoginPage(): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, isLoading, router])

  return (
    <AuthGuard requireAuth={false}>
      <AppShell>
        <div className="mx-auto flex max-w-md flex-col items-center justify-center py-12">
          <div className="w-full rounded-2xl border border-blue-100 bg-white/90 p-8 shadow-sm">
            <div className="text-center">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-blue-600 text-2xl font-bold text-white shadow">
                AI
              </div>
              <h1 className="mb-2 text-2xl font-semibold text-blue-900">
                AI English Trainer
              </h1>
              <p className="mb-8 text-sm text-blue-700">
                インタラクティブな英語学習を始めましょう
              </p>
              
              <div className="space-y-4">
                <LoginButton className="w-full" size="lg">
                  ログインして開始する
                </LoginButton>
                
                <div className="text-xs text-blue-600">
                  <p>ログインすることで、以下の機能をご利用いただけます：</p>
                  <ul className="mt-2 space-y-1 text-left">
                    <li>• パーソナライズされた学習セッション</li>
                    <li>• 進捗の保存と復習システム</li>
                    <li>• AIによる即時フィードバック</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </AppShell>
    </AuthGuard>
  )
}
