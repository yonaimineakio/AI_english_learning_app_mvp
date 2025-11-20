export type ScenarioCategory = 'travel' | 'business' | 'daily'

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced'

export type SessionMode = 'quick' | 'standard' | 'deep' | 'custom'

export type ScenarioFilterCategory = ScenarioCategory | 'all'

export interface ScenarioSummary {
  id: number
  name: string
  description: string
  category: ScenarioCategory
  difficulty: DifficultyLevel
  estimatedMinutes: number
}

export interface ScenarioDetail extends ScenarioSummary {
  learningGoals: string[]
  sampleDialog: string
  // シナリオごとに重点的に覚えたい動詞句・熟語（キーフレーズ）
  keyPhrases?: string[]
}

export interface ScenarioPreset {
  label: string
  rounds: number
  description: string
  estimatedMinutes: number
  mode: SessionMode
}

export interface ScenarioSelectionState {
  selectedScenarioId?: number
  selectedRounds: number
  selectedDifficulty: DifficultyLevel
  mode: SessionMode
  estimatedMinutes: number
}

export const ROUND_PRESETS: ScenarioPreset[] = [
  {
    label: 'Quick',
    rounds: 4,
    description: '短時間で要点だけを復習したいときに',
    estimatedMinutes: 12,
    mode: 'quick',
  },
  {
    label: 'Standard',
    rounds: 6,
    description: '標準的な学習コース',
    estimatedMinutes: 18,
    mode: 'standard',
  },
  {
    label: 'Deep',
    rounds: 10,
    description: 'じっくりアウトプットとフィードバックを受けたいときに',
    estimatedMinutes: 30,
    mode: 'deep',
  },
]

export const DEFAULT_SCENARIO_SELECTION: ScenarioSelectionState = {
  selectedScenarioId: undefined,
  selectedRounds: ROUND_PRESETS[1].rounds,
  selectedDifficulty: 'intermediate',
  mode: 'standard',
  estimatedMinutes: ROUND_PRESETS[1].estimatedMinutes,
}

export const MIN_ROUNDS = 4
export const MAX_ROUNDS = 12

export const estimateMinutes = (rounds: number) => rounds * 3

