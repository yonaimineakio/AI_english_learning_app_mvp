"use client"

import { useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { useAudioRecording } from '@/hooks/use-audio-recording'
import { transcribeAudio } from '@/lib/session'

interface AudioRecorderProps {
  onTranscriptionComplete: (text: string) => void
  onError: (error: string) => void
  disabled?: boolean
  className?: string
}

export function AudioRecorder({ 
  onTranscriptionComplete, 
  onError, 
  disabled = false,
  className = '' 
}: AudioRecorderProps) {
  const [isTranscribing, setIsTranscribing] = useState(false)
  const {
    isRecording,
    isProcessing,
    isAutoStopping,
    startRecording,
    stopRecording,
    error,
    elapsedSeconds,
    silenceDurationSeconds,
    silenceThresholdSeconds,
  } = useAudioRecording({
    onRecordingComplete: async (blob) => {
      setIsTranscribing(true)
      try {
        const audioFile = new File([blob], 'recording.webm', { type: 'audio/webm' })
        const result = await transcribeAudio(audioFile)
        onTranscriptionComplete(result.text)
      } catch (err) {
        console.error('Transcription error:', err)
        onError(err instanceof Error ? err.message : '音声認識に失敗しました')
      } finally {
        setIsTranscribing(false)
      }
    }
  })

  const silenceProgress = useMemo(() => {
    if (!isRecording || silenceThresholdSeconds <= 0) return 0
    const progress = Math.min((silenceDurationSeconds / silenceThresholdSeconds) * 100, 100)
    return Number(progress.toFixed(1))
  }, [isRecording, silenceDurationSeconds, silenceThresholdSeconds])

  const handleStartRecording = async () => {
    try {
      await startRecording()
    } catch (err) {
      onError('録音の開始に失敗しました')
    }
  }

  const handleStopRecording = () => {
    stopRecording({ force: true })
  }



  // エラー表示
  if (error) {
    return (
      <div className={`rounded-lg border border-red-200 bg-red-50 p-4 ${className}`}>
        <p className="text-sm text-red-600">{error}</p>
        <div className="mt-3 flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => window.location.reload()}
          >
            ページを再読み込み
          </Button>
        </div>
        <p className="mt-2 text-xs text-red-500">
          音声録音が利用できない場合は、テキスト入力をご利用ください。
        </p>
      </div>
    )
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* 録音ボタン */}
      <div className="flex gap-2">
        {!isRecording && (
          <Button
            onClick={handleStartRecording}
            disabled={disabled || isTranscribing}
            className="flex items-center gap-2"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
            録音開始
          </Button>
        )}

        {isRecording && (
          <Button
            onClick={handleStopRecording}
            className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white"
          >
            <div className="h-2 w-2 rounded-full bg-white animate-pulse" />
            録音停止
          </Button>
        )}
      </div>

      {/* 録音中の表示 */}
      {isRecording && (
        <div className="flex flex-col gap-1 text-sm text-blue-600">
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="h-1 w-1 rounded-full bg-blue-500 animate-pulse" />
              <div className="h-1 w-1 rounded-full bg-blue-500 animate-pulse" style={{ animationDelay: '0.2s' }} />
              <div className="h-1 w-1 rounded-full bg-blue-500 animate-pulse" style={{ animationDelay: '0.4s' }} />
            </div>
            録音中... 話してください
            <span className="text-xs text-blue-500">{elapsedSeconds.toFixed(1)} 秒</span>
          </div>
          <div className="h-1 w-full rounded bg-blue-100">
            <div
              className="h-1 rounded bg-blue-500 transition-all"
              style={{ width: `${silenceProgress}%` }}
            />
          </div>
          <span className="text-xs text-blue-500">
            {isAutoStopping
              ? '無音が続いたため録音を停止しています...'
              : `無音が${silenceThresholdSeconds}秒続くと自動で停止します（現在 ${silenceDurationSeconds.toFixed(1)} 秒）`}
          </span>
        </div>
      )}

      {/* 処理中の表示 */}
      {isProcessing && (
        <div className="flex items-center gap-2 text-sm text-blue-600">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          音声を処理中...
        </div>
      )}

      {/* 文字起こし中の表示 */}
      {isTranscribing && (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-green-600 border-t-transparent" />
          音声を認識中...
        </div>
      )}
    </div>
  )
}
