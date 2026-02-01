"use client"

import { useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { PlusIcon, SparklesIcon } from '@heroicons/react/24/outline'

import { ScenarioCategoryFilter } from '@/components/scenario/scenario-category-filter'
import { ScenarioCard } from '@/components/scenario/scenario-card'
import { CustomScenarioCard } from '@/components/scenario/custom-scenario-card'
import { ScenarioDetailDialog } from '@/components/scenario/scenario-detail-dialog'
import { CreateCustomScenarioDialog } from '@/components/scenario/create-custom-scenario-dialog'
import { RoundSelector } from '@/components/scenario/round-selector'
import { ScenarioSummaryPanel } from '@/components/scenario/scenario-summary-panel'
import { SCENARIO_LIST } from '@/lib/scenarios'
import { fetchCustomScenarios, deleteCustomScenario } from '@/lib/custom-scenarios'
import {
  DEFAULT_SCENARIO_SELECTION,
  ScenarioFilterCategory,
  ScenarioSelectionState,
  CustomScenario,
} from '@/types/scenario'
import { calculateEstimatedMinutes } from '@/lib/utils'
import { startSession } from '@/lib/session'

interface ScenarioPageProps {
  placementLevel?: 'beginner' | 'intermediate' | 'advanced'
}

export function ScenarioPage({ placementLevel }: ScenarioPageProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [selectedScenarioId, setSelectedScenarioId] = useState<number | undefined>(
    DEFAULT_SCENARIO_SELECTION.selectedScenarioId
  )
  const [selectedCustomScenarioId, setSelectedCustomScenarioId] = useState<number | undefined>(
    DEFAULT_SCENARIO_SELECTION.selectedCustomScenarioId
  )
  const [selectionState, setSelectionState] = useState<ScenarioSelectionState>(DEFAULT_SCENARIO_SELECTION)
  const [filterCategory, setFilterCategory] = useState<ScenarioFilterCategory>('all')
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [detailScenarioId, setDetailScenarioId] = useState<number | undefined>(undefined)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  // カスタムシナリオ一覧を取得
  const { data: customScenariosData } = useQuery({
    queryKey: ['customScenarios'],
    queryFn: () => fetchCustomScenarios(),
  })
  const customScenarios = customScenariosData?.custom_scenarios ?? []

  // 削除ミューテーション
  const deleteMutation = useMutation({
    mutationFn: deleteCustomScenario,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customScenarios'] })
      // 選択中のカスタムシナリオが削除された場合はクリア
      if (selectedCustomScenarioId === deletingId) {
        setSelectedCustomScenarioId(undefined)
        setSelectionState((prev) => ({
          ...prev,
          selectedCustomScenarioId: undefined,
        }))
      }
      setDeletingId(null)
    },
    onError: () => {
      setDeletingId(null)
    },
  })

  const handleDeleteCustomScenario = (id: number) => {
    if (window.confirm('このシナリオを削除しますか？')) {
      setDeletingId(id)
      deleteMutation.mutate(id)
    }
  }

  const startMutation = useMutation({
    mutationFn: () => {
      if (!selectionState.selectedScenarioId && !selectionState.selectedCustomScenarioId) {
        throw new Error('シナリオが選択されていません')
      }
      return startSession({
        scenarioId: selectionState.selectedScenarioId,
        customScenarioId: selectionState.selectedCustomScenarioId,
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
    // オリジナルフィルターの場合は空配列を返す（カスタムシナリオのみ表示）
    if (filterCategory === 'original') return []

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
    setSelectedCustomScenarioId(undefined) // カスタムシナリオ選択をクリア
    const scenario = SCENARIO_LIST.find((item) => item.id === scenarioId)
    if (scenario) {
      setSelectionState((prev) => ({
        ...prev,
        selectedScenarioId: scenarioId,
        selectedCustomScenarioId: undefined,
        selectedDifficulty: scenario.difficulty, // シナリオの難易度を自動設定
        estimatedMinutes: calculateEstimatedMinutes(prev.selectedRounds),
      }))
    }
  }

  const handleSelectCustomScenario = (customScenarioId: number) => {
    setSelectedCustomScenarioId(customScenarioId)
    setSelectedScenarioId(undefined) // 通常シナリオ選択をクリア
    setSelectionState((prev) => ({
      ...prev,
      selectedScenarioId: undefined,
      selectedCustomScenarioId: customScenarioId,
      selectedDifficulty: 'intermediate', // カスタムシナリオは intermediate 固定
      estimatedMinutes: calculateEstimatedMinutes(prev.selectedRounds),
    }))
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
    setSelectedCustomScenarioId(DEFAULT_SCENARIO_SELECTION.selectedCustomScenarioId)
    setSelectionState(DEFAULT_SCENARIO_SELECTION)
    setFilterCategory('all')
  }

  const handleConfirm = () => {
    if ((!selectionState.selectedScenarioId && !selectionState.selectedCustomScenarioId) || startMutation.isPending) return
    startMutation.mutate()
  }

  const selectedScenario = selectedScenarioId
    ? SCENARIO_LIST.find((scenario) => scenario.id === selectedScenarioId)
    : undefined

  const selectedCustomScenario = selectedCustomScenarioId
    ? customScenarios.find((scenario) => scenario.id === selectedCustomScenarioId)
    : undefined

  // サマリーパネルに表示するシナリオ情報
  const summaryScenario = selectedScenario ?? (selectedCustomScenario ? {
    id: selectedCustomScenario.id,
    name: selectedCustomScenario.name,
    description: selectedCustomScenario.description,
    category: 'daily' as const, // カスタムシナリオのデフォルトカテゴリ
    difficulty: 'intermediate' as const,
    estimatedMinutes: selectionState.estimatedMinutes,
  } : undefined)

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50 pb-12">
      <div className="mx-auto max-w-6xl px-4 pt-8">
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
            {/* オリジナルシナリオ作成ボタン */}
            <div className="mb-6">
              <button
                type="button"
                onClick={() => setCreateDialogOpen(true)}
                className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-md transition hover:from-purple-700 hover:to-blue-700 hover:shadow-lg"
              >
                <SparklesIcon className="h-5 w-5" />
                オリジナルシナリオを作成
              </button>
            </div>

            <div className="mb-6 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">シナリオを選ぶ</h2>
                <p className="mt-1 text-sm text-gray-500">
                  カテゴリで絞り込み、詳細を確認しながら最適なシナリオを選択できます。
                  {placementLevel ? `（現在のレベル: ${placementLevel}）` : null}
                </p>
              </div>
              <ScenarioCategoryFilter
                selectedCategory={filterCategory}
                onSelectCategory={setFilterCategory}
                hasCustomScenarios={customScenarios.length > 0}
              />
            </div>

            {/* カスタムシナリオ表示（オリジナルフィルターまたは全て表示時） */}
            {(filterCategory === 'original' || filterCategory === 'all') && customScenarios.length > 0 && (
              <div className="mb-6">
                {filterCategory === 'all' && (
                  <h3 className="mb-3 flex items-center gap-2 text-sm font-medium text-purple-700">
                    <SparklesIcon className="h-4 w-4" />
                    あなたのオリジナルシナリオ
                  </h3>
                )}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {customScenarios.map((scenario) => (
                    <CustomScenarioCard
                      key={`custom-${scenario.id}`}
                      scenario={scenario}
                      isSelected={scenario.id === selectedCustomScenarioId}
                      onSelect={handleSelectCustomScenario}
                      onDelete={handleDeleteCustomScenario}
                      isDeleting={deletingId === scenario.id}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* オリジナルフィルター時にシナリオがない場合のメッセージ */}
            {filterCategory === 'original' && customScenarios.length === 0 && (
              <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 py-12">
                <SparklesIcon className="h-10 w-10 text-gray-300" />
                <p className="mt-3 text-sm text-gray-500">まだオリジナルシナリオがありません</p>
                <button
                  type="button"
                  onClick={() => setCreateDialogOpen(true)}
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-purple-700"
                >
                  <PlusIcon className="h-4 w-4" />
                  シナリオを作成
                </button>
              </div>
            )}

            {/* 通常シナリオ表示 */}
            {filterCategory !== 'original' && (
              <>
                {filterCategory === 'all' && customScenarios.length > 0 && (
                  <h3 className="mb-3 text-sm font-medium text-gray-700">すべてのシナリオ</h3>
                )}
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
              </>
            )}
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
              selectedScenario={summaryScenario}
              selectionState={selectionState}
              onConfirm={handleConfirm}
              onReset={handleReset}
              isConfirmDisabled={(!selectedScenario && !selectedCustomScenario) || startMutation.isPending}
              isLoading={startMutation.isPending}
            />
          </section>
        </div>
      </div>

      <ScenarioDetailDialog scenarioId={detailScenarioId} open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} />
      <CreateCustomScenarioDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSuccess={() => {
          // オリジナルフィルターに切り替えて新しいシナリオを表示
          setFilterCategory('original')
        }}
      />

      {startError ? (
        <div className="mx-auto mt-6 w-full max-w-xl rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {startError}
        </div>
      ) : null}
    </div>
  )
}

