import { SCENARIO_CATEGORIES } from '@/lib/scenarios'
import { cn } from '@/lib/utils'
import { ScenarioFilterCategory } from '@/types/scenario'
import { SparklesIcon } from '@heroicons/react/24/outline'

interface ScenarioCategoryFilterProps {
  selectedCategory: ScenarioFilterCategory
  onSelectCategory: (category: ScenarioFilterCategory) => void
  hasCustomScenarios?: boolean
}

export function ScenarioCategoryFilter({
  selectedCategory,
  onSelectCategory,
  hasCustomScenarios = false,
}: ScenarioCategoryFilterProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      <button
        type="button"
        onClick={() => onSelectCategory('all')}
        className={cn(
          'rounded-full border px-4 py-1 text-sm transition whitespace-nowrap',
          selectedCategory === 'all'
            ? 'border-blue-600 bg-blue-50 text-blue-600'
            : 'border-gray-200 text-gray-600 hover:border-gray-300'
        )}
      >
        すべて
      </button>
      {SCENARIO_CATEGORIES.map((category) => (
        <button
          key={category.id}
          type="button"
          onClick={() => onSelectCategory(category.id as ScenarioFilterCategory)}
          className={cn(
            'rounded-full border px-4 py-1 text-sm transition whitespace-nowrap',
            selectedCategory === category.id
              ? 'border-blue-600 bg-blue-50 text-blue-600'
              : 'border-gray-200 text-gray-600 hover:border-gray-300'
          )}
        >
          {category.label}
        </button>
      ))}
      {/* オリジナルシナリオフィルター */}
      <button
        type="button"
        onClick={() => onSelectCategory('original')}
        className={cn(
          'flex items-center gap-1.5 rounded-full border px-4 py-1 text-sm transition whitespace-nowrap',
          selectedCategory === 'original'
            ? 'border-purple-600 bg-purple-50 text-purple-600'
            : 'border-gray-200 text-gray-600 hover:border-gray-300'
        )}
      >
        <SparklesIcon className="h-4 w-4" />
        オリジナル
        {hasCustomScenarios && (
          <span className="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-purple-100 text-[10px] font-medium text-purple-700">
            !
          </span>
        )}
      </button>
    </div>
  )
}

