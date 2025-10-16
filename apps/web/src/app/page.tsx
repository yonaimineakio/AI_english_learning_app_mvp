import { Suspense } from 'react'

import { ScenarioPage } from '@/components/scenario/scenario-page'
import { AppShell } from '@/components/layout/app-shell'
import { AuthGuard } from '@/components/auth/auth-guard'

export default function Home() {
  return (
    <AuthGuard requireAuth={true}>
      <AppShell>
        <Suspense fallback={<div className="p-8 text-center text-sm text-blue-600">読み込み中…</div>}>
          <ScenarioPage />
        </Suspense>
      </AppShell>
    </AuthGuard>
  )
}
