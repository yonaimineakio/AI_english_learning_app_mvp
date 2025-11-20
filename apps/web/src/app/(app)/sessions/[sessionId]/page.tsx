"use client"

import { Fragment, useCallback, useState } from 'react'
import { notFound, useParams, useRouter } from 'next/navigation'
import { Dialog, Transition } from '@headlessui/react'

import { AudioRecorder } from '@/components/audio/audio-recorder'
import { ConversationTurnRow } from '@/components/conversation/conversation-turn'
import { ExtendModal } from '@/components/session/extend-modal'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useSessionConversation } from '@/hooks/use-session-conversation'
import { getScenarioDetail } from '@/lib/scenarios'
import { formatMinutes } from '@/lib/utils'

export default function SessionConversationPage(): JSX.Element {
  const params = useParams<{ sessionId: string }>()
  const router = useRouter()
  const sessionId = Number(params.sessionId)

  if (Number.isNaN(sessionId)) {
    notFound()
  }

  const [message, setMessage] = useState('')
  const [expandedTurnId, setExpandedTurnId] = useState<string | null>(null)
  const [isExtendModalOpen, setIsExtendModalOpen] = useState(false)
  const [isAutoEnd, setIsAutoEnd] = useState(false)
  const [audioError, setAudioError] = useState<string | null>(null)
  const [isLearningGoalsOpen, setIsLearningGoalsOpen] = useState(false)

  const {
    turns,
    status,
    isLoadingStatus,
    submitMessage,
    extendSession: extendSessionAction,
    endSession: endSessionAction,
    pending,
    extendPending,
    endPending,
    error,
    estimatedMinutes,
  } = useSessionConversation({
    sessionId,
    onSessionEnd: () => {
      // 通常の終了時（サイドバーの「セッションを終了する」ボタンなど）
      router.push(`/summary?sessionId=${sessionId}`)
    },
    onRoundCompleted: (isAutoEndDetected = false) => {
      setIsAutoEnd(isAutoEndDetected)
      setIsExtendModalOpen(true)
    },
  })

  const scenarioDetail = status?.scenarioId ? getScenarioDetail(status.scenarioId) : null

  const handleSubmit = useCallback(() => {
    if (!message.trim() || pending || !status?.isActive) return
    submitMessage(message)
    setMessage('')
  }, [message, pending, status?.isActive, submitMessage])

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      handleSubmit()
    }
  }

  const handleExtendModalClose = useCallback(() => {
    setIsExtendModalOpen(false)
    setIsAutoEnd(false)
  }, [])

  const handleExtendModalExtend = useCallback(() => {
    extendSessionAction(() => {
      // 延長成功後にモーダルを閉じる
      setIsExtendModalOpen(false)
    })
  }, [extendSessionAction])

  const handleExtendModalEnd = useCallback(() => {
    // 「セッションを終了する」ボタン → ホーム画面に遷移
    endSessionAction(() => {
      router.push('/')
    })
  }, [endSessionAction, router])

  const handleExtendModalReview = useCallback(() => {
    // 「復習する」ボタン → サマリーページに遷移
    endSessionAction(() => {
      router.push(`/summary?sessionId=${sessionId}`)
    })
  }, [endSessionAction, router, sessionId])

  const handleTranscriptionComplete = useCallback((text: string) => {
    setMessage(text)
    setAudioError(null)
  }, [])

  const handleAudioError = useCallback((error: string) => {
    setAudioError(error)
  }, [])

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-white via-blue-50 to-blue-100">
      <header className="border-b border-blue-100 bg-white/80">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-blue-500">AI Conversation Session</p>
            <h1 className="text-lg font-semibold text-blue-900">
              {status?.scenarioName ?? '会話セッション'}
            </h1>
          </div>
          <div className="text-sm text-blue-600">
            {isLoadingStatus ? '読み込み中…' : `${status?.completedRounds ?? 0}/${status?.roundTarget ?? 0} ラウンド`}
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-4 px-4 py-6 lg:flex-row">
        <section className="flex flex-1 flex-col gap-4">
          <div className="flex-1 overflow-y-auto rounded-2xl border border-blue-100 bg-white/90 p-4 shadow-sm">
            {turns.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center text-blue-700">
                <p className="text-lg font-semibold">会話を始めましょう</p>
                <p className="mt-2 text-sm">入力欄に英語で話しかける内容を入力して送信してください。</p>
              </div>
            ) : (
              <div className="space-y-4">
                {turns.map((turn) => (
                  <ConversationTurnRow
                    key={turn.id}
                    turn={turn}
                    isDetailsOpen={expandedTurnId === turn.id}
                    onToggleDetails={() =>
                      setExpandedTurnId((prev) => (prev === turn.id ? null : turn.id))
                    }
                  />
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-blue-100 bg-white/95 p-4 shadow-sm">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <Input
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="英語で発話内容を入力してください"
                className="flex-1"
                disabled={pending || status?.isActive === false || isExtendModalOpen}
              />
              <Button
                onClick={handleSubmit}
                disabled={!!status && !status.isActive || isExtendModalOpen}
                className="w-full sm:w-auto"
              >
                {pending ? '送信中…' : '送信'}
              </Button>
            </div>
            
            {/* 音声録音機能 */}
            <div className="mt-3">
              <AudioRecorder
                onTranscriptionComplete={handleTranscriptionComplete}
                onError={handleAudioError}
                disabled={pending || status?.isActive === false || isExtendModalOpen}
              />
            </div>
            
            {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
            {audioError ? <p className="mt-2 text-sm text-red-600">{audioError}</p> : null}
            {status?.isActive === false ? (
              <p className="mt-2 text-sm text-blue-600">
                セッションは終了しました。復習ページに移動して確認しましょう。
              </p>
            ) : null}
            
            {/* 自動終了時の通知を追加 */}
            {turns.length > 0 && turns[turns.length - 1].shouldEndSession ? (
              <p className="mt-2 text-sm text-green-600">
                会話を終了します。お疲れ様でした！
              </p>
            ) : null}
          </div>
        </section>

        <aside className="grid w-full max-w-xl gap-4 lg:w-80">
          <div className="rounded-2xl border border-blue-200 bg-white/95 p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-blue-900">セッション情報</h2>
            <div className="mt-3 space-y-2 text-sm text-blue-800">
              <p>シナリオ: {status?.scenarioName ?? '---'}</p>
              <p>難易度: {status?.difficultyLabel ?? status?.difficulty}</p>
              <p>モード: {status?.modeLabel ?? status?.mode}</p>
              <p>
                進捗: {status?.completedRounds ?? 0}/{status?.roundTarget ?? 0} ラウンド
              </p>
              <p>残り時間の目安: {formatMinutes(estimatedMinutes)}</p>
            </div>

            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-blue-100">
              <div
                className="h-full rounded-full bg-blue-500"
                style={{
                  width: `${Math.min(
                    ((status?.completedRounds ?? 0) / (status?.roundTarget ?? 1)) * 100,
                    100,
                  ).toFixed(1)}%`,
                }}
              />
            </div>

            <div className="mt-4 flex flex-col gap-2">
              <Button
                variant="outline"
                onClick={() => extendSessionAction()}
                disabled={!status?.canExtend || extendPending}
              >
                {extendPending ? '延長中…' : '+3ラウンド延長'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => endSessionAction()}
                disabled={endPending}
              >
                {endPending ? '終了処理中…' : 'セッションを終了する'}
              </Button>
              {scenarioDetail ? (
                <Button
                  type="button"
                  variant="ghost"
                  className="mt-1 justify-start text-xs text-blue-700 hover:text-blue-900"
                  onClick={() => setIsLearningGoalsOpen(true)}
                >
                  このセッションの学習ゴールを見る
                </Button>
              ) : null}
            </div>
          </div>

          <div className="space-y-3 rounded-2xl border border-blue-200 bg-white/95 p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-blue-900">最新の改善例文</h2>
            <p className="text-sm text-blue-800">
              {(() => {
                const lastTurnWithFeedback = [...turns].reverse().find((t) => t.roundIndex > 0)
                return lastTurnWithFeedback
                  ? lastTurnWithFeedback.aiReply.improvedSentence
                  : '会話を開始するとここに表示されます'
              })()}
            </p>
            <p className="text-xs text-blue-600">
              3回音読してニュアンスを確かめましょう。必要に応じて類例を作って練習してください。
            </p>
          </div>

          <div className="space-y-3 rounded-2xl border border-blue-200 bg-white/95 p-4 shadow-sm">
            <h2 className="text-sm font-semibold text-blue-900">フィードバック活用のヒント</h2>
            <ul className="list-disc space-y-2 pl-5 text-sm text-blue-800">
              <li>120字以内の短評を意識して次の発話に活かす</li>
              <li>改善例文を声に出して練習し、差分を確認する</li>
              <li>タグをもとに重点ポイントを振り返る</li>
            </ul>
          </div>
        </aside>
      </main>

      {/* 延長確認モーダル */}
      <ExtendModal
        isOpen={isExtendModalOpen}
        onClose={handleExtendModalClose}
        onExtend={handleExtendModalExtend}
        onEnd={handleExtendModalEnd}
        onReview={isAutoEnd ? handleExtendModalReview : undefined}
        canExtend={status?.canExtend ?? false}
        isExtending={extendPending}
        isEnding={endPending}
        completedRounds={status?.completedRounds ?? 0}
        roundTarget={status?.roundTarget ?? 0}
        isAutoEnd={isAutoEnd}
      />

      {/* 学習ゴールモーダル */}
      {scenarioDetail && scenarioDetail.learningGoals?.length ? (
        <Transition.Root show={isLearningGoalsOpen} as={Fragment}>
          <Dialog
            as="div"
            className="relative z-50"
            onClose={() => setIsLearningGoalsOpen(false)}
          >
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0"
              enterTo="opacity-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100"
              leaveTo="opacity-0"
            >
              <div className="fixed inset-0 bg-gray-900/30 backdrop-blur-sm" />
            </Transition.Child>

            <div className="fixed inset-0 z-50 overflow-y-auto">
              <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-6">
                <Transition.Child
                  as={Fragment}
                  enter="ease-out duration-200"
                  enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                  enterTo="opacity-100 translate-y-0 sm:scale-100"
                  leave="ease-in duration-150"
                  leaveFrom="opacity-100 translate-y-0 sm:scale-100"
                  leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
                >
                  <Dialog.Panel className="relative w-full max-w-lg transform overflow-hidden rounded-2xl bg-white text-left shadow-xl transition-all">
                    <div className="border-b border-gray-100 px-6 py-5">
                      <Dialog.Title className="text-base font-semibold text-gray-900">
                        このセッションの学習ゴール
                      </Dialog.Title>
                      <p className="mt-1 text-xs text-gray-500">
                        {scenarioDetail.name}
                      </p>
                    </div>
                    <div className="space-y-5 px-6 py-5">
                      <div>
                        <h3 className="text-xs font-semibold text-gray-500">学習ゴール</h3>
                        <ul className="mt-2 list-inside list-disc space-y-2 text-sm text-gray-700">
                          {scenarioDetail.learningGoals.map((goal) => (
                            <li key={goal}>{goal}</li>
                          ))}
                        </ul>
                      </div>

                      {scenarioDetail.keyPhrases?.length ? (
                        <div>
                          <h3 className="text-xs font-semibold text-gray-500">キーフレーズ</h3>
                          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-gray-800">
                            {scenarioDetail.keyPhrases.map((phrase) => (
                              <li key={phrase}>{phrase}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null}
                    </div>
                    <div className="border-t border-gray-100 bg-gray-50 px-6 py-4">
                      <button
                        type="button"
                        className="w-full rounded-lg border border-gray-200 bg-white py-2 text-sm font-medium text-gray-700 transition hover:border-gray-300"
                        onClick={() => setIsLearningGoalsOpen(false)}
                      >
                        閉じる
                      </button>
                    </div>
                  </Dialog.Panel>
                </Transition.Child>
              </div>
            </div>
          </Dialog>
        </Transition.Root>
      ) : null}
    </div>
  )
}


