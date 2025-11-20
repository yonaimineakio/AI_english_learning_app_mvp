"use client"

import { Suspense, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'

import { ScenarioPage } from '@/components/scenario/scenario-page'
import { AppShell } from '@/components/layout/app-shell'
import { AuthGuard } from '@/components/auth/auth-guard'
import { apiRequest } from '@/lib/api-client'

interface CurrentUser {
  id: number
  name: string
  email: string
  placement_level?: 'beginner' | 'intermediate' | 'advanced'
  placement_completed_at?: string | null
}

export default function Home() {
  const router = useRouter()

  const { data: user, isLoading } = useQuery({
    queryKey: ['current-user'],
    queryFn: () => apiRequest<CurrentUser>('/auth/me', 'GET'),
  })

  useEffect(() => {
    if (!isLoading && user && !user.placement_completed_at) {
      router.replace('/placement')
    }
  }, [isLoading, user, router])

  const shouldShowPlacement = !isLoading && user && !user.placement_completed_at

  if (shouldShowPlacement) {
    return null
  }

  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <Suspense fallback={<div className="p-8 text-center text-sm text-blue-600">読み込み中…</div>}>
          <ScenarioPage placementLevel={user?.placement_level} />
        </Suspense>
      </AppShell>
    </AuthGuard>
  )
}
