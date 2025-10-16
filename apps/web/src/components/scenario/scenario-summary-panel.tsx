import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScenarioSelectionState, ScenarioSummary } from '@/types/scenario'
import { formatMinutes } from '@/lib/utils'

interface ScenarioSummaryPanelProps {
  selectedScenario?: ScenarioSummary
  selectionState: ScenarioSelectionState
  onConfirm: () => void
  onReset: () => void
  isConfirmDisabled?: boolean
  isLoading?: boolean
}

export function ScenarioSummaryPanel({
  selectedScenario,
  selectionState,
  onConfirm,
  onReset,
  isConfirmDisabled,
  isLoading,
}: ScenarioSummaryPanelProps) {
  const totalMinutes = formatMinutes(selectionState.selectedRounds * 3)
  const difficultyLabel =
    selectionState.selectedDifficulty === 'beginner'
      ? '初級'
      : selectionState.selectedDifficulty === 'intermediate'
      ? '中級'
      : '上級'

  return (
    <aside className="flex h-full min-h-[240px] flex-col justify-between rounded-2xl bg-white p-6 shadow-lg">
      <div className="space-y-4">
        <div>
          <div className="text-sm font-semibold uppercase tracking-wide text-blue-600">セッション概要</div>
          <h3 className="mt-1 text-2xl font-bold text-gray-900">学習プランを確認</h3>
          <p className="mt-3 text-sm text-gray-500">開始前に選択内容を確認し、準備ができたらセッションをスタートしましょう。</p>
        </div>

        <div className="space-y-3 rounded-xl bg-gray-50 p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">シナリオ</span>
            <span className="text-sm font-medium text-gray-900">
              {selectedScenario ? selectedScenario.name : 'シナリオが未選択です'}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">ラウンド数</span>
            <span className="text-sm font-medium text-gray-900">
              {selectionState.selectedRounds}ラウンド ({totalMinutes})
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">難易度</span>
            <Badge>{difficultyLabel}</Badge>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <h4 className="text-sm font-semibold text-gray-800">学習のヒント</h4>
          <ul className="mt-3 space-y-2 text-xs text-gray-500">
            <li>・ラウンドごとのAIフィードバックで改善点を確認しながら進めましょう。</li>
            <li>・気になったフレーズはメモを取っておくと復習がスムーズです。</li>
            <li>・時間が足りない場合はセッション中に最大2回まで延長できます。</li>
          </ul>
        </div>
      </div>

      <div className="mt-6 space-y-3">
        <Button size="lg" className="w-full" onClick={onConfirm} disabled={isConfirmDisabled}>
          {isLoading ? '開始中…' : 'セッションを開始する'}
        </Button>
        <Button variant="ghost" size="lg" className="w-full" onClick={onReset}>
          選択内容をリセット
        </Button>
      </div>
    </aside>
  )
}

