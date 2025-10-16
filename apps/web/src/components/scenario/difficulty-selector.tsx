import { SegmentedControl } from '@/components/ui/segmented-control'
import { DifficultyLevel } from '@/types/scenario'

const difficultyOptions = [
  {
    label: '初級',
    value: 'beginner' as DifficultyLevel,
    description: '基本的なフレーズと安心感のあるフィードバック',
  },
  {
    label: '中級',
    value: 'intermediate' as DifficultyLevel,
    description: '自然な表現と丁寧なフィードバック',
  },
  {
    label: '上級',
    value: 'advanced' as DifficultyLevel,
    description: '高度な表現と提案型フィードバック',
  },
]

interface DifficultySelectorProps {
  value: DifficultyLevel
  onChange: (difficulty: DifficultyLevel) => void
}

export function DifficultySelector({ value, onChange }: DifficultySelectorProps) {
  return (
    <div className="space-y-3">
      <SegmentedControl
        value={value}
        onChange={(val) => onChange(val as DifficultyLevel)}
        options={difficultyOptions}
        size="lg"
      />
      <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-600">
        {value === 'beginner' && (
          <p>
            初級レベルでは基礎的な表現を丁寧に復習し、短く分かりやすいフィードバックが得られます。安心して会話に慣れていきたい方におすすめです。
          </p>
        )}
        {value === 'intermediate' && (
          <p>
            中級レベルでは自然な会話フローを意識しながら、ボキャブラリーの提案や言い回しの改善を行います。実践に近いアウトプット練習に最適です。
          </p>
        )}
        {value === 'advanced' && (
          <p>
            上級レベルではニュアンスやディスコース構造まで踏み込み、より高度な表現力を磨きます。議論やプレゼン力を伸ばしたい方に向いています。
          </p>
        )}
      </div>
    </div>
  )
}

