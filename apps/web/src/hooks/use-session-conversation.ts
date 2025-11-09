import { useCallback, useMemo, useState, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  fetchSessionStatus,
  submitTurn,
  extendSession,
  endSession,
} from '@/lib/session'
import { ConversationTurn } from '@/types/conversation'

interface UseSessionConversationOptions {
  sessionId: number
  onSessionEnd?: () => void
  onRoundCompleted?: (isAutoEnd?: boolean) => void
}

export function useSessionConversation({ sessionId, onSessionEnd, onRoundCompleted }: UseSessionConversationOptions) {
  const queryClient = useQueryClient()
  const [turns, setTurns] = useState<ConversationTurn[]>([])
  const [error, setError] = useState<string | null>(null)
  const [hasEnded, setHasEnded] = useState<boolean>(false)
  const [previousCompletedRounds, setPreviousCompletedRounds] = useState<number>(0)

  const statusQuery = useQuery({
    queryKey: ['session-status', sessionId],
    queryFn: () => fetchSessionStatus(sessionId),
    staleTime: 30_000,
  })

  const submitMutation = useMutation({
    mutationFn: (message: string) => submitTurn(sessionId, message),
    onMutate: async (message) => {
      setError(null)
      setTurns((prev) => [
        ...prev,
        {
          id: `pending-${Date.now()}`,
          roundIndex: prev.length + 1,
          userMessage: message,
          aiReply: {
            message: '応答を生成しています…',
            feedbackShort: '',
            improvedSentence: '',
            tags: [],
            scores: null,
            details: null,
            createdAt: new Date().toISOString(),
          },
          createdAt: new Date().toISOString(),
          isPending: true,
        },
      ])
    },
    onSuccess: ({ turn, status }) => {
      setTurns((prev) => {
        const next = [...prev]
        next[next.length - 1] = turn
        return next
      })
      if (status) {
        queryClient.setQueryData(['session-status', sessionId], status)
      }
      
      // 自動終了判定
      if (turn.shouldEndSession) {
        // 少し遅延させてユーザーがAI応答を読めるようにする
        setTimeout(() => {
          if (onRoundCompleted) {
            onRoundCompleted(true)  // 自動終了であることを伝える
          } else if (onSessionEnd) {
            // フォールバック: onRoundCompletedが指定されていない場合は直接終了
            setHasEnded(true)
            onSessionEnd()
          }
        }, 2000)
      }
    },
    onError: (err) => {
      setTurns((prev) => prev.filter((turn) => !turn.isPending))
      setError(err instanceof Error ? err.message : '送信に失敗しました')
    },
    onSettled: () => {
      void statusQuery.refetch()
    },
  })

  const onExtendSuccessRef = useRef<(() => void) | null>(null)
  const onEndSuccessRef = useRef<(() => void) | null>(null)

  const extendMutation = useMutation({
    mutationFn: () => extendSession(sessionId),
    onSuccess: (status) => {
      queryClient.setQueryData(['session-status', sessionId], status)
      if (onExtendSuccessRef.current) {
        onExtendSuccessRef.current()
        onExtendSuccessRef.current = null
      }
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : '延長に失敗しました')
      onExtendSuccessRef.current = null
    },
    onSettled: () => {
      void statusQuery.refetch()
    },
  })

  const endMutation = useMutation({
    mutationFn: () => endSession(sessionId),
    onSuccess: () => {
      setHasEnded(true)
      // 成功時のコールバックがあればそれを呼ぶ
      if (onEndSuccessRef.current) {
        onEndSuccessRef.current()
        onEndSuccessRef.current = null
      } else if (onSessionEnd) {
        // フォールバック: 通常の終了時（サイドバーのボタンなど）
        onSessionEnd()
      }
      void statusQuery.refetch()
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : '終了に失敗しました')
      setHasEnded(false)
      onEndSuccessRef.current = null
    },
  })

  const remainingRounds = useMemo(() => {
    if (!statusQuery.data) return 0
    return Math.max(statusQuery.data.roundTarget - statusQuery.data.completedRounds, 0)
  }, [statusQuery.data])

  const estimatedMinutes = useMemo(() => remainingRounds * 3, [remainingRounds])

  // ラウンド完了の検知
  useEffect(() => {
    const currentCompletedRounds = statusQuery.data?.completedRounds ?? 0
    const roundTarget = statusQuery.data?.roundTarget ?? 0
    
    // 規定ラウンド数に達した場合、かつ前回より増加している場合
    if (
      currentCompletedRounds >= roundTarget &&
      currentCompletedRounds > previousCompletedRounds &&
      statusQuery.data?.isActive &&
      onRoundCompleted
    ) {
      onRoundCompleted()
    }
    
    setPreviousCompletedRounds(currentCompletedRounds)
  }, [statusQuery.data?.completedRounds, statusQuery.data?.roundTarget, statusQuery.data?.isActive, previousCompletedRounds, onRoundCompleted])

  const submitMessage = useCallback(
    (message: string) => {
      if (!message.trim() || submitMutation.isPending || !statusQuery.data?.isActive) return
      submitMutation.mutate(message.trim())
    },
    [submitMutation, statusQuery.data?.isActive],
  )


  return {
    turns,
    status: statusQuery.data,
    isLoadingStatus: statusQuery.isLoading,
    submitMessage,
    extendSession: (onSuccess?: () => void) => {
      if (hasEnded || endMutation.isPending || extendMutation.isPending) return
      onExtendSuccessRef.current = onSuccess ?? null
      extendMutation.mutate()
    },
    endSession: (onSuccess?: () => void) => {
      if (endMutation.isPending) return
      onEndSuccessRef.current = onSuccess ?? null
      setHasEnded(true)
      endMutation.mutate()
    },
    pending: submitMutation.isPending,
    extendPending: extendMutation.isPending,
    endPending: endMutation.isPending,
    error,
    setError,
    estimatedMinutes,
    remainingRounds,
  }
}


