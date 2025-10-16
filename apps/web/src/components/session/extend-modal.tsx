"use client"

import { useState } from 'react'

import { Button } from '@/components/ui/button'

interface ExtendModalProps {
  isOpen: boolean
  onClose: () => void
  onExtend: () => void
  onEnd: () => void
  canExtend: boolean
  isExtending: boolean
  isEnding: boolean
  completedRounds: number
  roundTarget: number
}

export function ExtendModal({
  isOpen,
  onClose,
  onExtend,
  onEnd,
  canExtend,
  isExtending,
  isEnding,
  completedRounds,
  roundTarget,
}: ExtendModalProps): JSX.Element | null {
  const [isClosing, setIsClosing] = useState(false)

  if (!isOpen) return null

  const handleClose = () => {
    setIsClosing(true)
    setTimeout(() => {
      setIsClosing(false)
      onClose()
    }, 150)
  }

  const handleExtend = () => {
    onExtend()
    handleClose()
  }

  const handleEnd = () => {
    onEnd()
    handleClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className={`absolute inset-0 bg-black/50 transition-opacity duration-150 ${
          isClosing ? 'opacity-0' : 'opacity-100'
        }`}
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div
        className={`relative mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-xl transition-all duration-150 ${
          isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'
        }`}
      >
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
            <svg
              className="h-6 w-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          
          <h2 className="mb-2 text-xl font-semibold text-blue-900">
            規定ラウンド完了
          </h2>
          
          <p className="mb-6 text-sm text-blue-700">
            {completedRounds}/{roundTarget} ラウンドが完了しました。
            <br />
            セッションを延長するか終了するか選択してください。
          </p>

          <div className="space-y-3">
            {canExtend && (
              <Button
                onClick={handleExtend}
                disabled={isExtending || isEnding}
                className="w-full"
                size="lg"
              >
                {isExtending ? '延長中…' : '+3ラウンド延長する'}
              </Button>
            )}
            
            <Button
              onClick={handleEnd}
              variant="outline"
              disabled={isExtending || isEnding}
              className="w-full"
              size="lg"
            >
              {isEnding ? '終了処理中…' : 'セッションを終了する'}
            </Button>
          </div>

          {!canExtend && (
            <p className="mt-4 text-xs text-blue-600">
              延長回数の上限に達しているため、終了のみ選択可能です。
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
