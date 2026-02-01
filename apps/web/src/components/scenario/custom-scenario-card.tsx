import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { CustomScenario } from '@/types/scenario'
import { TrashIcon, SparklesIcon } from '@heroicons/react/24/outline'

interface CustomScenarioCardProps {
  scenario: CustomScenario
  isSelected: boolean
  onSelect: (scenarioId: number) => void
  onDelete: (scenarioId: number) => void
  isDeleting?: boolean
}

export function CustomScenarioCard({
  scenario,
  isSelected,
  onSelect,
  onDelete,
  isDeleting = false,
}: CustomScenarioCardProps) {
  return (
    <Card
      className={`flex h-full flex-col overflow-hidden border transition hover:border-purple-200 ${
        isSelected ? 'border-purple-400 shadow-lg shadow-purple-50' : 'border-gray-200'
      }`}
    >
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-purple-500" />
            <CardTitle className="text-lg text-gray-900">{scenario.name}</CardTitle>
          </div>
          <Badge className="bg-purple-50 text-purple-700">オリジナル</Badge>
        </div>
        <CardDescription className="text-sm text-gray-600">{scenario.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col justify-between space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>あなたの役割</span>
            <span className="truncate text-gray-700">{scenario.user_role}</span>
          </div>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>AIの役割</span>
            <span className="truncate text-gray-700">{scenario.ai_role}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant={isSelected ? 'primary' : 'secondary'}
            size="full"
            onClick={() => onSelect(scenario.id)}
            className="flex-1"
          >
            {isSelected ? '選択中' : 'このシナリオを選択'}
          </Button>
          <button
            type="button"
            onClick={() => onDelete(scenario.id)}
            disabled={isDeleting}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-gray-200 text-gray-400 transition hover:border-red-200 hover:bg-red-50 hover:text-red-500 disabled:opacity-50"
            title="シナリオを削除"
          >
            {isDeleting ? (
              <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              <TrashIcon className="h-4 w-4" />
            )}
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
