import { forwardRef } from 'react'

import { cn } from '@/lib/utils'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  description?: string
  suffix?: React.ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, description, suffix, id, ...props }, ref) => {
    return (
      <div className={cn('w-full', className)}>
        {label && (
          <label htmlFor={id} className="mb-1 block text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <div className="relative">
          <input
            ref={ref}
            id={id}
            className={cn(
              'block w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100',
              error && 'border-red-300 focus:border-red-500 focus:ring-red-100'
            )}
            {...props}
          />
          {suffix && <span className="absolute inset-y-0 right-3 flex items-center text-sm text-gray-400">{suffix}</span>}
        </div>
        {description && <p className="mt-1 text-xs text-gray-500">{description}</p>}
        {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
      </div>
    )
  }
)

Input.displayName = 'Input'

export { Input }

