"use client"

import { useCallback, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'

interface WordPuzzleProps {
  wordOptions: string[]
  distractorWords: string[]
  onSubmit: (answer: string) => void
  disabled?: boolean
  className?: string
}

export function WordPuzzle({
  wordOptions,
  distractorWords,
  onSubmit,
  disabled = false,
  className = '',
}: WordPuzzleProps) {
  const [selectedWords, setSelectedWords] = useState<string[]>([])
  const [availableWords, setAvailableWords] = useState<string[]>(() => {
    // Shuffle all words (correct + distractors)
    const allWords = [...wordOptions, ...distractorWords]
    return shuffleArray(allWords)
  })

  // Shuffle function
  function shuffleArray<T>(array: T[]): T[] {
    const shuffled = [...array]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    return shuffled
  }

  const handleWordClick = useCallback((word: string, index: number) => {
    if (disabled) return
    
    // Remove from available and add to selected
    setAvailableWords((prev) => {
      const newAvailable = [...prev]
      newAvailable.splice(index, 1)
      return newAvailable
    })
    setSelectedWords((prev) => [...prev, word])
  }, [disabled])

  const handleSelectedWordClick = useCallback((word: string, index: number) => {
    if (disabled) return
    
    // Remove from selected and add back to available
    setSelectedWords((prev) => {
      const newSelected = [...prev]
      newSelected.splice(index, 1)
      return newSelected
    })
    setAvailableWords((prev) => [...prev, word])
  }, [disabled])

  const handleReset = useCallback(() => {
    if (disabled) return
    
    // Reset to initial shuffled state
    const allWords = [...wordOptions, ...distractorWords]
    setAvailableWords(shuffleArray(allWords))
    setSelectedWords([])
  }, [disabled, wordOptions, distractorWords])

  const handleSubmit = useCallback(() => {
    if (disabled || selectedWords.length === 0) return
    
    const answer = selectedWords.join(' ')
    onSubmit(answer)
  }, [disabled, selectedWords, onSubmit])

  const canSubmit = useMemo(() => {
    return selectedWords.length > 0 && !disabled
  }, [selectedWords.length, disabled])

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Selected words area (answer) */}
      <div className="min-h-[80px] rounded-lg border-2 border-dashed border-blue-300 bg-blue-50/50 p-3">
        <p className="mb-2 text-xs font-medium text-blue-600">あなたの回答:</p>
        <div className="flex flex-wrap gap-1.5">
          {selectedWords.length === 0 ? (
            <p className="text-sm text-blue-400">下の単語をタップして文を組み立ててください</p>
          ) : (
            selectedWords.map((word, index) => (
              <button
                key={`selected-${word}-${index}`}
                type="button"
                onClick={() => handleSelectedWordClick(word, index)}
                disabled={disabled}
                className="inline-flex items-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {word}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Available words area */}
      <div className="rounded-lg border border-blue-100 bg-white p-3">
        <p className="mb-2 text-xs font-medium text-blue-600">使用する単語:</p>
        <div className="flex flex-wrap gap-1.5">
          {availableWords.length === 0 ? (
            <p className="text-sm text-blue-400">すべての単語を使用しました</p>
          ) : (
            availableWords.map((word, index) => (
              <button
                key={`available-${word}-${index}`}
                type="button"
                onClick={() => handleWordClick(word, index)}
                disabled={disabled}
                className="inline-flex items-center rounded-md border border-blue-200 bg-white px-3 py-1.5 text-sm font-medium text-blue-800 shadow-sm transition-all hover:border-blue-400 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {word}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleReset}
          disabled={disabled}
        >
          リセット
        </Button>
        <Button
          type="button"
          size="sm"
          onClick={handleSubmit}
          disabled={!canSubmit}
        >
          回答を確認
        </Button>
      </div>
    </div>
  )
}
