"use client"

import { useState } from 'react'

import { SegmentedControl } from '@/components/ui/segmented-control'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { calculateEstimatedMinutes, formatMinutes } from '@/lib/utils'
import {
  DEFAULT_SCENARIO_SELECTION,
  MAX_ROUNDS,
  MIN_ROUNDS,
  ROUND_PRESETS,
  ScenarioSelectionState,
  ScenarioPreset,
  SessionMode,
} from '@/types/scenario'

interface RoundSelectorProps {
  selectedRounds: number
  selectedMode: ScenarioSelectionState['mode']
  onChange: (rounds: number, mode: ScenarioSelectionState['mode']) => void
}

const modeOptions: { label: string; value: SessionMode; description?: string }[] = [
  { label: 'Quick', value: 'quick', description: '4ラウンド / 約12分' },
  { label: 'Standard', value: 'standard', description: '6ラウンド / 約18分' },
  { label: 'Deep', value: 'deep', description: '10ラウンド / 約30分' },
  { label: 'カスタム', value: 'custom', description: '4〜12ラウンドから選択' },
]

export function RoundSelector({ selectedMode, selectedRounds, onChange }: RoundSelectorProps) {
  const [customRounds, setCustomRounds] = useState(() =>
    selectedMode === 'custom' ? selectedRounds : DEFAULT_SCENARIO_SELECTION.selectedRounds
  )

  const handleModeChange = (mode: ScenarioSelectionState['mode']) => {
    if (mode === 'custom') {
      onChange(customRounds, mode)
    } else {
      const preset = ROUND_PRESETS.find((preset) => preset.mode === mode)
      onChange(preset?.rounds ?? DEFAULT_SCENARIO_SELECTION.selectedRounds, mode)
    }
  }

  const handleCustomRoundsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(event.target.value)
    if (Number.isNaN(value)) return

    const clampedValue = Math.min(Math.max(value, MIN_ROUNDS), MAX_ROUNDS)
    setCustomRounds(clampedValue)
    onChange(clampedValue, 'custom')
  }

  const activePreset: ScenarioPreset | undefined =
    selectedMode !== 'custom'
      ? ROUND_PRESETS.find((preset) => preset.rounds === selectedRounds)
      : undefined

  return (
    <div className="space-y-4">
      <div>
        <SegmentedControl value={selectedMode} options={modeOptions} onChange={handleModeChange} size="lg" />
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {ROUND_PRESETS.map((preset) => {
          const isActive = selectedMode !== 'custom' && preset.rounds === selectedRounds
          return (
            <button
              key={preset.label}
              type="button"
              onClick={() => onChange(preset.rounds, preset.mode)}
              className={`flex h-full flex-col rounded-xl border p-4 text-left transition ${
                isActive ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="text-base font-semibold text-gray-900">{preset.label}</div>
                <Badge variant={isActive ? 'default' : 'outline'}>{preset.rounds}ラウンド</Badge>
              </div>
              <p className="mt-2 flex-1 text-sm text-gray-600">{preset.description}</p>
              <div className="mt-3 text-sm font-medium text-gray-700">
                所要時間: {formatMinutes(preset.estimatedMinutes)}
              </div>
            </button>
          )
        })}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-800">カスタム設定</h3>
          <Badge variant="outline">範囲: {MIN_ROUNDS}〜{MAX_ROUNDS}ラウンド</Badge>
        </div>
        <div className="mt-3 grid gap-4 md:grid-cols-[auto_1fr] md:items-center">
          <Input
            id="custom-rounds"
            type="number"
            min={MIN_ROUNDS}
            max={MAX_ROUNDS}
            value={customRounds}
            onChange={handleCustomRoundsChange}
            aria-label="ラウンド数"
            suffix="ラウンド"
            className="max-w-[120px]"
          />
          <div className="text-sm text-gray-500">
            <div className="font-medium text-gray-700">所要時間の目安</div>
            <div className="text-lg font-semibold text-blue-600">
              {formatMinutes(calculateEstimatedMinutes(customRounds))}
            </div>
            <p className="mt-1 text-xs text-gray-400">1ラウンドあたり約3分で計算</p>
          </div>
        </div>
      </div>

      {activePreset && (
        <div className="rounded-xl bg-blue-50 p-4 text-sm text-blue-800">
          <div className="font-semibold">{activePreset.label}プランを選択中</div>
          <p className="mt-1">
            {activePreset.rounds}ラウンド（{formatMinutes(activePreset.estimatedMinutes)}）でしっかり学習できます。
          </p>
        </div>
      )}
    </div>
  )
}

