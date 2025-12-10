"use client"

import { useId } from 'react'

import { ConversationTurn } from '@/types/conversation'

interface ConversationTurnProps {
  turn: ConversationTurn
  isDetailsOpen: boolean
  onToggleDetails: () => void
}

export function ConversationTurnRow({ turn, isDetailsOpen, onToggleDetails }: ConversationTurnProps) {
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
                <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">改善例文</p>
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


