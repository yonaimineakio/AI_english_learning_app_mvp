export type ScenarioCategory = 'travel' | 'business' | 'daily'

export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced'

export type SessionMode = 'quick' | 'standard' | 'deep' | 'custom'

export type ScenarioFilterCategory = ScenarioCategory | 'all' | 'original'

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
  selectedCustomScenarioId?: number  // カスタムシナリオID
  selectedRounds: number
  selectedDifficulty: DifficultyLevel
  mode: SessionMode
  estimatedMinutes: number
}

// カスタムシナリオ（オリジナルシナリオ）の型定義
export interface CustomScenario {
  id: number
  user_id: string
  name: string
  description: string
  user_role: string
  ai_role: string
  difficulty: string
  is_active: boolean
  created_at: string
}

export interface CustomScenarioCreate {
  name: string
  description: string
  user_role: string
  ai_role: string
}

export interface CustomScenarioListResponse {
  custom_scenarios: CustomScenario[]
  total_count: number
}

export interface CustomScenarioLimitResponse {
  daily_limit: number
  created_today: number
  remaining: number
  is_pro: boolean
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
  selectedCustomScenarioId: undefined,
  selectedRounds: ROUND_PRESETS[1].rounds,
  selectedDifficulty: 'intermediate',
  mode: 'standard',
  estimatedMinutes: ROUND_PRESETS[1].estimatedMinutes,
}

export const MIN_ROUNDS = 4
export const MAX_ROUNDS = 12

export const estimateMinutes = (rounds: number) => rounds * 3

