"use client"

import { ReactNode } from 'react'

import { cn } from '@/lib/utils'
import { AuthStatus } from '@/components/auth/auth-status'

interface AppShellProps {
  children: ReactNode
  className?: string
}

export function AppShell({ children, className }: AppShellProps): JSX.Element {
  return (
    <div className={cn('min-h-screen bg-gradient-to-br from-white via-blue-50 to-blue-100', className)}>
      <header className="border-b border-blue-100 bg-white/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-lg font-bold text-white shadow">
              AI
            </div>
            <div>
              <p className="text-sm font-semibold text-blue-900">AI English Trainer</p>
              <p className="text-xs text-blue-600">インタラクティブ英語学習</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-blue-600">
            <span className="hidden rounded-full border border-blue-200 px-3 py-1 sm:block">セッション準備</span>
            <span className="rounded-full border border-blue-200 px-3 py-1">Asia/Tokyo</span>
            <AuthStatus className="ml-2" />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>

      <footer className="border-t border-blue-100 bg-white/70">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-4 text-xs text-blue-600 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <span>© {new Date().getFullYear()} AI English Learning MVP</span>
          <span>すべてのセッションがAsia/Tokyoタイムゾーンで管理されます</span>
        </div>
      </footer>
    </div>
  )
}


