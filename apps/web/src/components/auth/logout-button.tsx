"use client"

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'

interface LogoutButtonProps {
  className?: string
  children?: React.ReactNode
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
}

export function LogoutButton({ className, children, variant = 'outline' }: LogoutButtonProps): JSX.Element {
  const { logout, isLoading } = useAuth()

  return (
    <Button 
      onClick={logout} 
      disabled={isLoading}
      variant={variant}
      className={className}
    >
      {isLoading ? 'ログアウト中...' : (children || 'ログアウト')}
    </Button>
  )
}
