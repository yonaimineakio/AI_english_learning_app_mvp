"use client"

import { useMemo } from 'react'
import type { WordMatch } from '@/lib/placement'

interface WordMatchDisplayProps {
  wordMatches: WordMatch[]
  score: number
  matchedCount: number
  totalCount: number
  className?: string
}

export function WordMatchDisplay({
  wordMatches,
  score,
  matchedCount,
  totalCount,
  className = '',
}: WordMatchDisplayProps) {
  const scoreColor = useMemo(() => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }, [score])

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Word matches display */}
      <div className="flex flex-wrap gap-1.5">
        {wordMatches.map((match, index) => (
          <span
            key={`${match.word}-${index}`}
            className={`inline-flex items-center rounded-md px-2 py-1 text-sm font-medium transition-colors ${
              match.matched
                ? 'bg-green-100 text-green-800 border border-green-200'
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}
          >
            {match.word}
          </span>
        ))}
      </div>

      {/* Score display */}
      <div className="flex items-center gap-4 rounded-lg bg-blue-50 px-4 py-2">
        <div className="flex-1">
          <div className="h-2 w-full rounded-full bg-blue-200">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>
        <div className={`text-sm font-semibold ${scoreColor}`}>
          {matchedCount}/{totalCount} ({score.toFixed(0)}%)
        </div>
      </div>
    </div>
  )
}
