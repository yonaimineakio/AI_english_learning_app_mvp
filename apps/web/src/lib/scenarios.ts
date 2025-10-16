import { ScenarioDetail, ScenarioSummary } from '@/types/scenario'

export const SCENARIO_CATEGORIES = [
  {
    id: 'travel',
    label: '旅行',
    description: '空港・ホテル・移動など旅行時の会話を想定',
  },
  {
    id: 'business',
    label: 'ビジネス',
    description: 'ミーティング・商談・メール対応など',
  },
  {
    id: 'daily',
    label: '日常会話',
    description: '日常生活でよく使う会話を中心に',
  },
]

export const SCENARIO_LIST: ScenarioSummary[] = [
  {
    id: 1,
    name: '空港チェックイン',
    description: 'チェックインから搭乗までの一連の流れを練習',
    category: 'travel',
    difficulty: 'beginner',
    estimatedMinutes: 18,
  },
  {
    id: 2,
    name: 'ビジネスミーティング',
    description: '会議での発言や合意形成に必要な表現を学習',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  },
  {
    id: 3,
    name: 'レストランでの注文',
    description: '予約から注文、会計までの会話パターンを習得',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 12,
  },
  {
    id: 4,
    name: 'オンライン商談',
    description: 'リモートミーティングでの説明や質問に対応',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 30,
  },
  {
    id: 5,
    name: 'ホテルチェックイン',
    description: '予約確認から要望の伝え方までを網羅',
    category: 'travel',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
  },
]

export const SCENARIO_DETAILS: Record<number, ScenarioDetail> = {
  1: {
    id: 1,
    name: '空港チェックイン',
    description: '空港での各場面で使える実践的なフレーズを学びます',
    category: 'travel',
    difficulty: 'beginner',
    estimatedMinutes: 18,
    learningGoals: [
      '旅の始まりに必要な表現を定着させる',
      'チェックイン時のやりとりに自信を持つ',
      '予期せぬ質問にも対応できる力をつける',
    ],
    sampleDialog: 'I have a reservation under the name Suzuki. Can I have a window seat, please?',
  },
  2: {
    id: 2,
    name: 'ビジネスミーティング',
    description: '会議で必要な表現とコミュニケーションスキルを身につけます',
    category: 'business',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
    learningGoals: [
      '意見を明確に述べる表現を習得',
      '合意形成のためのフレーズを練習',
      '質問に対する対応力を強化',
    ],
    sampleDialog: 'From my perspective, we should prioritize the user experience over new features at this stage.',
  },
  3: {
    id: 3,
    name: 'レストランでの注文',
    description: '飲食店での様々な場面に対応できる表現を学びます',
    category: 'daily',
    difficulty: 'beginner',
    estimatedMinutes: 12,
    learningGoals: [
      'メニューを理解し適切に注文する力をつける',
      'アレルギーや好みの説明に慣れる',
      '会計時のやり取りをスムーズに行う',
    ],
    sampleDialog: 'Could you recommend something vegetarian? I’m allergic to nuts.',
  },
  4: {
    id: 4,
    name: 'オンライン商談',
    description: 'リモート環境での商談に必要な表現とマナーを習得します',
    category: 'business',
    difficulty: 'advanced',
    estimatedMinutes: 30,
    learningGoals: [
      'オンラインでの自己紹介とアイスブレイクに慣れる',
      '提案内容を説得力を持って伝える',
      'フォローアップとアクションアイテムを明確にする',
    ],
    sampleDialog: 'Let’s recap the action items and confirm the next steps for both teams.',
  },
  5: {
    id: 5,
    name: 'ホテルチェックイン',
    description: '宿泊時に必要なコミュニケーションスキルを磨きます',
    category: 'travel',
    difficulty: 'intermediate',
    estimatedMinutes: 18,
    learningGoals: [
      '予約内容の確認と要望の伝え方を練習',
      'トラブル対応時の英語表現に慣れる',
      'チェックアウト時の手続きをスムーズにする',
    ],
    sampleDialog: 'Is it possible to have a late checkout tomorrow around 2 PM?',
  },
}

export const getScenarioDetail = (id: number): ScenarioDetail | null => {
  return SCENARIO_DETAILS[id] ?? null
}

