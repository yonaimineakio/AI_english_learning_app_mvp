"use client"

import { useId } from 'react'

import { ConversationTurn } from '@/types/conversation'

interface ConversationTurnProps {
  turn: ConversationTurn
  isDetailsOpen: boolean
  onToggleDetails: () => void
  onSavePhrase?: () => void
  isSaved?: boolean
  isSaving?: boolean
}

export function ConversationTurnRow({
  turn,
  isDetailsOpen,
  onToggleDetails,
  onSavePhrase,
  isSaved = false,
  isSaving = false,
}: ConversationTurnProps) {
  const detailsId = useId()

  return (
    <article className="space-y-3" aria-label={`Conversation turn ${turn.roundIndex}`}>
      {turn.userMessage.trim() !== '' && (
        <div className="flex justify-end">
          <div className="max-w-[75%] rounded-2xl bg-blue-600 px-4 py-3 text-sm text-white shadow">
            <p className="text-xs font-semibold uppercase tracking-wide text-blue-100" aria-label="Your message">
              You
            </p>
            <p className="mt-1 text-sm text-white/90">{turn.userMessage}</p>
          </div>
        </div>
      )}

      <div className="flex items-start gap-3">
        <div className="h-9 w-9 rounded-full bg-blue-100 text-blue-700 shadow-inner" aria-hidden>
          <span className="flex h-full w-full items-center justify-center text-sm font-semibold">AI</span>
        </div>
        <div className="flex-1 space-y-3">
          <div className="rounded-2xl border border-blue-100 bg-white/90 p-4 shadow">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-500" aria-label="AI response">
                AI の応答
              </p>
              <p className="mt-2 text-sm text-blue-900">{turn.aiReply.message}</p>
            </div>
          </div>

          {turn.roundIndex > 0 && (
            <div className="rounded-2xl border border-blue-100 bg-blue-50/80 p-4 shadow">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p
                    className="text-xs font-semibold uppercase tracking-wide text-blue-500"
                    aria-label="Feedback summary"
                  >
                    フィードバック
                  </p>
                  <p className="mt-1 text-sm text-blue-900">{turn.aiReply.feedbackShort}</p>
                </div>
                <button
                  type="button"
                  onClick={onToggleDetails}
                  className="text-xs font-semibold text-blue-600 underline"
                  aria-expanded={isDetailsOpen}
                  aria-controls={detailsId}
                >
                  {isDetailsOpen ? '閉じる' : '詳細'}
                </button>
              </div>

              <div className="mt-3 rounded-xl bg-white/90 p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">改善例文</p>
                  {onSavePhrase && (
                    <button
                      type="button"
                      onClick={onSavePhrase}
                      disabled={isSaved || isSaving}
                      className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium transition ${
                        isSaved
                          ? 'bg-green-100 text-green-700'
                          : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                      } ${isSaving ? 'opacity-50' : ''}`}
                    >
                      {isSaved ? (
                        <>
                          <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                          保存済み
                        </>
                      ) : isSaving ? (
                        '保存中...'
                      ) : (
                        <>
                          <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                            />
                          </svg>
                          保存
                        </>
                      )}
                    </button>
                  )}
                </div>
                <p className="mt-1 text-sm text-blue-900">{turn.aiReply.improvedSentence}</p>
              </div>

              {turn.aiReply.tags?.length ? (
                <div className="mt-3 flex flex-wrap gap-2" aria-label="Feedback tags">
                  {turn.aiReply.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              ) : null}

              {isDetailsOpen && turn.aiReply.details ? (
                <div id={detailsId} className="mt-3 rounded-xl border border-blue-200 bg-white/95 p-3">
                  {turn.aiReply.details.explanation ? (
                    <p className="text-sm text-blue-900">{turn.aiReply.details.explanation}</p>
                  ) : null}
                  {turn.aiReply.details.suggestions?.length ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-blue-800">
                      {turn.aiReply.details.suggestions.map((suggestion) => (
                        <li key={suggestion}>{suggestion}</li>
                      ))}
                    </ul>
                  ) : null}
                  {turn.aiReply.scores ? (
                    <dl className="mt-3 grid grid-cols-2 gap-2 text-sm text-blue-800">
                      {turn.aiReply.scores.pronunciation !== null && (
                        <div>
                          <dt className="text-xs text-blue-500">発音</dt>
                          <dd className="text-sm font-semibold">{turn.aiReply.scores.pronunciation}</dd>
                        </div>
                      )}
                      {turn.aiReply.scores.grammar !== null && (
                        <div>
                          <dt className="text-xs text-blue-500">文法</dt>
                          <dd className="text-sm font-semibold">{turn.aiReply.scores.grammar}</dd>
                        </div>
                      )}
                    </dl>
                  ) : null}
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </article>
  )
}


