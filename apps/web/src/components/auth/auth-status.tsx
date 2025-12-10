"use client"

import { useRouter } from 'next/navigation'

import { useAuth } from '@/hooks/use-auth'
import { LoginButton } from './login-button'
import { LogoutButton } from './logout-button'

interface AuthStatusProps {
  className?: string
}

export function AuthStatus({ className }: AuthStatusProps): JSX.Element {
  const router = useRouter()
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        <span className="text-sm text-blue-600">認証中...</span>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <span className="text-sm text-blue-600">未ログイン</span>
        <LoginButton />
      </div>
    )
  }

  const handleProfileClick = () => {
    router.push('/settings')
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <button
        type="button"
        onClick={handleProfileClick}
        className="flex items-center gap-2 rounded-full border border-transparent px-2 py-1 text-left transition hover:border-blue-300 hover:bg-blue-50"
      >
        {user.picture && (
          <img
            src={user.picture}
            alt={user.name}
            className="h-6 w-6 rounded-full"
          />
        )}
        <div className="text-sm">
          <div className="font-medium text-blue-900">{user.name}</div>
          <div className="text-xs text-blue-600">{user.email}</div>
        </div>
      </button>
      <LogoutButton />
    </div>
  )
}
