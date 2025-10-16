"use client"

import { useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

export default function CallbackPage(): JSX.Element {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(true)
  const hasHandledRef = useRef(false)
  const { setAuthData } = useAuth()

  useEffect(() => {
    const code = searchParams.get('code')
    const authError = searchParams.get('error')

    if (hasHandledRef.current) {
      return
    }

    if (!code && !authError) {
      return
    }

    hasHandledRef.current = true

    const handleCallback = async () => {
      try {
        if (authError) {
          setError(`認証エラー: ${authError}`)
          setIsProcessing(false)
          return
        }

        if (!code) {
          setError('認証コードが取得できませんでした')
          setIsProcessing(false)
          return
        }

        // 認証コードをバックエンドに送信してトークンを取得
        const apiBaseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '')
        const response = await fetch(`${apiBaseUrl}/auth/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        })

        if (!response.ok) {
          throw new Error('認証に失敗しました')
        }

        const data = await response.json()
        
        // トークンとユーザー情報を保存
        setAuthData(data.access_token, data.user)
        
        // メインページにリダイレクト
        router.push('/')
      } catch (err) {
        console.error('Callback error:', err)
        setError(err instanceof Error ? err.message : '認証処理中にエラーが発生しました')
        setIsProcessing(false)
      }
    }

    handleCallback()
  }, [searchParams, router, setAuthData])

  if (isProcessing) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="text-sm text-blue-600">認証処理中...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-red-600">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h1 className="mb-2 text-lg font-semibold text-gray-900">認証エラー</h1>
          <p className="mb-4 text-sm text-gray-600">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            ホームに戻る
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <div className="mb-4 text-green-600">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="mb-2 text-lg font-semibold text-gray-900">認証完了</h1>
        <p className="text-sm text-gray-600">リダイレクト中...</p>
      </div>
    </div>
  )
}
