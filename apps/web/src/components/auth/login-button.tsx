"use client"

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'

interface LoginButtonProps {
  className?: string
  children?: React.ReactNode
}

export function LoginButton({ className, children }: LoginButtonProps): JSX.Element {
  const { login, isLoading } = useAuth()

  return (
    <Button 
      onClick={login} 
      disabled={isLoading}
      className={className}
    >
      {isLoading ? 'ログイン中...' : (children || 'ログイン')}
    </Button>
  )
}
