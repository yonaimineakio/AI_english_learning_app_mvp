import { Suspense } from 'react'

import { AppShell } from '@/components/layout/app-shell'
import { ReviewQuiz } from '@/components/review/review-quiz'

export default function ReviewPage(): JSX.Element {
  return (
    <AppShell>
      <div className="mx-auto flex max-w-3xl flex-col gap-6">
        <h1 className="text-xl font-semibold text-blue-900">復習タイム</h1>
        <p className="text-sm text-blue-600">昨日のセッションからピックアップした改善フレーズを復習しましょう。</p>
        <Suspense fallback={<div className="p-4 text-blue-600">読み込み中…</div>}>
          <ReviewQuiz />
        </Suspense>
      </div>
    </AppShell>
  )
}

