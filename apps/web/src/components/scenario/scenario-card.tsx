import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScenarioSummary } from '@/types/scenario'
import { formatMinutes } from '@/lib/utils'

interface ScenarioCardProps {
  scenario: ScenarioSummary
  isSelected: boolean
  onSelect: (scenarioId: number) => void
}

const difficultyColorMap: Record<ScenarioSummary['difficulty'], string> = {
  beginner: 'bg-emerald-50 text-emerald-700',
  intermediate: 'bg-amber-50 text-amber-700',
  advanced: 'bg-purple-50 text-purple-700',
}

export function ScenarioCard({ scenario, isSelected, onSelect }: ScenarioCardProps) {
  return (
    <Card
      className={`flex h-full flex-col overflow-hidden border transition hover:border-blue-200 ${
        isSelected ? 'border-blue-400 shadow-lg shadow-blue-50' : 'border-gray-200'
      }`}
    >
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg text-gray-900">{scenario.name}</CardTitle>
          <Badge className={difficultyColorMap[scenario.difficulty]}>{
            scenario.difficulty === 'beginner'
              ? '初級'
              : scenario.difficulty === 'intermediate'
              ? '中級'
              : '上級'
          }</Badge>
        </div>
        <CardDescription className="text-sm text-gray-600">{scenario.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col justify-between space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>カテゴリ</span>
            <span>
              {scenario.category === 'travel'
                ? '旅行'
                : scenario.category === 'business'
                ? 'ビジネス'
                : '日常会話'}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>所要時間目安</span>
            <span className="font-medium text-gray-700">{formatMinutes(scenario.estimatedMinutes)}</span>
          </div>
        </div>
        <Button
          variant={isSelected ? 'primary' : 'secondary'}
          size="full"
          onClick={() => onSelect(scenario.id)}
        >
          {isSelected ? '選択中' : 'このシナリオを選択'}
        </Button>
      </CardContent>
    </Card>
  )
}

