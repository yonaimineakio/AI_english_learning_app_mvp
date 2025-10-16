"use client"

import { useId } from 'react'

import { cn } from '@/lib/utils'

interface SegmentedControlOption<TValue extends string | number> {
  label: string
  value: TValue
  description?: string
}

interface SegmentedControlProps<TValue extends string | number> {
  name?: string
  value: TValue
  options: SegmentedControlOption<TValue>[]
  onChange: (value: TValue) => void
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function SegmentedControl<TValue extends string | number>({
  name,
  value,
  options,
  onChange,
  className,
  size = 'md',
}: SegmentedControlProps<TValue>) {
  const id = useId()

  return (
    <div className={cn('flex items-center justify-between rounded-xl bg-gray-50 p-1', className)}>
      {options.map((option) => {
        const isActive = option.value === value
        return (
          <label
            key={option.value}
            htmlFor={`${id}-${option.value}`}
            className={cn(
              'flex-1 cursor-pointer rounded-lg border border-transparent px-3 py-2 text-center transition-all duration-150',
              'focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-200',
              isActive ? 'bg-white shadow-sm border-blue-200 text-blue-700' : 'text-gray-500 hover:text-gray-700'
            )}
          >
            <input
              type="radio"
              id={`${id}-${option.value}`}
              name={name ?? id}
              value={option.value}
              checked={isActive}
              onChange={() => onChange(option.value)}
              className="sr-only"
            />
            <div>
              <div
                className={cn(
                  'text-sm font-medium',
                  size === 'lg' && 'text-base',
                  size === 'sm' && 'text-xs'
                )}
              >
                {option.label}
              </div>
              {option.description && (
                <div className="mt-1 text-xs text-gray-400">{option.description}</div>
              )}
            </div>
          </label>
        )
      })}
    </div>
  )
}

