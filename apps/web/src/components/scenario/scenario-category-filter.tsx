import { SCENARIO_CATEGORIES } from '@/lib/scenarios'
import { cn } from '@/lib/utils'
import { ScenarioFilterCategory } from '@/types/scenario'

interface ScenarioCategoryFilterProps {
  selectedCategory: ScenarioFilterCategory
  onSelectCategory: (category: ScenarioFilterCategory) => void
}

export function ScenarioCategoryFilter({ selectedCategory, onSelectCategory }: ScenarioCategoryFilterProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      <button
        type="button"
        onClick={() => onSelectCategory('all')}
        className={cn(
          'rounded-full border px-4 py-1 text-sm transition',
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
            'rounded-full border px-4 py-1 text-sm transition',
            selectedCategory === category.id
              ? 'border-blue-600 bg-blue-50 text-blue-600'
              : 'border-gray-200 text-gray-600 hover:border-gray-300'
          )}
        >
          <div className="font-medium">{category.label}</div>
          <div className="text-xs text-gray-400">{category.description}</div>
        </button>
      ))}
    </div>
  )
}

