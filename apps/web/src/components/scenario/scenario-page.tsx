"use client"

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'

import { ScenarioCategoryFilter } from '@/components/scenario/scenario-category-filter'
import { ScenarioCard } from '@/components/scenario/scenario-card'
import { ScenarioDetailDialog } from '@/components/scenario/scenario-detail-dialog'
import { RoundSelector } from '@/components/scenario/round-selector'
import { ScenarioSummaryPanel } from '@/components/scenario/scenario-summary-panel'
import { StreakDisplay } from '@/components/stats/streak-display'
import { SCENARIO_LIST } from '@/lib/scenarios'
import {
  DEFAULT_SCENARIO_SELECTION,
  ScenarioFilterCategory,
  ScenarioSelectionState,
} from '@/types/scenario'
import { calculateEstimatedMinutes } from '@/lib/utils'
import { startSession } from '@/lib/session'

interface ScenarioPageProps {
  placementLevel?: 'beginner' | 'intermediate' | 'advanced'
}

export function ScenarioPage({ placementLevel }: ScenarioPageProps) {
  const router = useRouter()
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | undefined>(
    DEFAULT_SCENARIO_SELECTION.selectedScenarioId
  )
  const [selectionState, setSelectionState] = useState<ScenarioSelectionState>(DEFAULT_SCENARIO_SELECTION)
  const [filterCategory, setFilterCategory] = useState<ScenarioFilterCategory>('all')
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [detailScenarioId, setDetailScenarioId] = useState<number | undefined>(undefined)
  const [startError, setStartError] = useState<string | null>(null)

  const startMutation = useMutation({
    mutationFn: () => {
      if (!selectionState.selectedScenarioId) {
        throw new Error('シナリオが選択されていません')
      }
      return startSession({
        scenarioId: selectionState.selectedScenarioId,
        roundTarget: selectionState.selectedRounds,
        difficulty: selectionState.selectedDifficulty,
        mode: selectionState.mode,
      })
    },
    onSuccess: (data) => {
      setStartError(null)
      router.push(`/sessions/${data.session_id}`)
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : 'セッション開始に失敗しました'
      setStartError(message)
    },
  })

  const filteredScenarios = useMemo(() => {
    let base = SCENARIO_LIST

    if (placementLevel === 'beginner') {
      base = base.filter((scenario) => scenario.difficulty === 'beginner')
    } else if (placementLevel === 'intermediate') {
      base = base.filter((scenario) => scenario.difficulty === 'beginner' || scenario.difficulty === 'intermediate')
    }

    if (filterCategory === 'all') return base
    return base.filter((scenario) => scenario.category === filterCategory)
  }, [filterCategory, placementLevel])

  const handleSelectScenario = (scenarioId: number) => {
    setSelectedScenarioId(scenarioId)
    const scenario = SCENARIO_LIST.find((item) => item.id === scenarioId)
    if (scenario) {
      setSelectionState((prev) => ({
        ...prev,
        selectedScenarioId: scenarioId,
        selectedDifficulty: scenario.difficulty, // シナリオの難易度を自動設定
        estimatedMinutes: calculateEstimatedMinutes(prev.selectedRounds),
      }))
    }
  }

  const handleShowDetails = (scenarioId: number) => {
    setDetailScenarioId(scenarioId)
    setDetailDialogOpen(true)
  }

  const handleRoundChange = (rounds: number, mode: ScenarioSelectionState['mode']) => {
    setSelectionState((prev) => ({
      ...prev,
      selectedRounds: rounds,
      mode,
      estimatedMinutes: calculateEstimatedMinutes(rounds),
    }))
  }

  const handleReset = () => {
    setSelectedScenarioId(DEFAULT_SCENARIO_SELECTION.selectedScenarioId)
    setSelectionState(DEFAULT_SCENARIO_SELECTION)
    setFilterCategory('all')
  }

  const handleConfirm = () => {
    if (!selectionState.selectedScenarioId || startMutation.isPending) return
    startMutation.mutate()
  }

  const selectedScenario = selectedScenarioId
    ? SCENARIO_LIST.find((scenario) => scenario.id === selectedScenarioId)
    : undefined

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50 pb-12">
      <div className="mx-auto max-w-6xl px-4 pt-8">
        {/* Stats Display */}
        <div className="mb-8">
          <StreakDisplay />
        </div>

        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-3 text-sm font-semibold uppercase tracking-wide text-blue-600">Step 1</div>
          <h1 className="text-3xl font-bold text-gray-900 md:text-4xl">
            学習したいシナリオとプランを選択しましょう
          </h1>
          <p className="mt-4 text-sm text-gray-600 md:text-base">
            カテゴリと難易度を選び、ラウンド数に応じた学習プランを作成します。所要時間は自動計算されるので、予定に合わせて調整できます。
          </p>
        </div>

        <div className="mt-10 space-y-12">
          <section>
            <div className="mb-6 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">シナリオを選ぶ</h2>
                <p className="mt-1 text-sm text-gray-500">
                  カテゴリで絞り込み、詳細を確認しながら最適なシナリオを選択できます。
                  {placementLevel ? `（現在のレベル: ${placementLevel}）` : null}
                </p>
              </div>
              <ScenarioCategoryFilter selectedCategory={filterCategory} onSelectCategory={setFilterCategory} />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredScenarios.map((scenario) => (
                <div key={scenario.id} className="relative">
                  <ScenarioCard
                    scenario={scenario}
                    isSelected={scenario.id === selectedScenarioId}
                    onSelect={handleSelectScenario}
                  />
                  <button
                    type="button"
                    className="absolute inset-x-0 bottom-4 text-center text-xs text-gray-400 underline"
                    onClick={() => handleShowDetails(scenario.id)}
                  >
                    詳細を表示
                  </button>
                </div>
              ))}
            </div>
          </section>

          <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <div className="space-y-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">ラウンド数と所要時間</h2>
                <p className="mt-1 text-sm text-gray-500">
                  プリセットから選択するか、自由にラウンド数を設定できます。1ラウンドあたり約3分で計算しています。
                </p>
              </div>
              <RoundSelector
                selectedMode={selectionState.mode}
                selectedRounds={selectionState.selectedRounds}
                onChange={handleRoundChange}
              />

            </div>

            <ScenarioSummaryPanel
              selectedScenario={selectedScenario}
              selectionState={selectionState}
              onConfirm={handleConfirm}
              onReset={handleReset}
              isConfirmDisabled={!selectedScenario || startMutation.isPending}
              isLoading={startMutation.isPending}
            />
          </section>
        </div>
      </div>

      <ScenarioDetailDialog scenarioId={detailScenarioId} open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} />

      {startError ? (
        <div className="mx-auto mt-6 w-full max-w-xl rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {startError}
        </div>
      ) : null}
    </div>
  )
}

