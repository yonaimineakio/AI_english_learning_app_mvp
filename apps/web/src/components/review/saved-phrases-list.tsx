"use client"

import { useCallback, useEffect, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { Fragment } from 'react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchSavedPhrases, deleteSavedPhrase, convertToReview } from '@/lib/saved-phrases'
import type { SavedPhrase } from '@/types/review'

export function SavedPhrasesList(): JSX.Element {
  const [phrases, setPhrases] = useState<SavedPhrase[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPhrase, setSelectedPhrase] = useState<SavedPhrase | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isConverting, setIsConverting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const loadPhrases = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetchSavedPhrases()
      setPhrases(response.savedPhrases)
      setTotalCount(response.totalCount)
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存した表現の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadPhrases()
  }, [loadPhrases])

  const handlePhraseClick = (phrase: SavedPhrase) => {
    setSelectedPhrase(phrase)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedPhrase(null)
  }

  const handleConvertToReview = async () => {
    if (!selectedPhrase) return

    setIsConverting(true)
    try {
      await convertToReview(selectedPhrase.id)
      // Update the phrase in the list
      setPhrases((prev) =>
        prev.map((p) =>
          p.id === selectedPhrase.id ? { ...p, convertedToReviewId: 1 } : p
        )
      )
      handleCloseModal()
    } catch (err) {
      setError(err instanceof Error ? err.message : '復習への変換に失敗しました')
    } finally {
      setIsConverting(false)
    }
  }

  const handleDelete = async () => {
    if (!selectedPhrase) return

    setIsDeleting(true)
    try {
      await deleteSavedPhrase(selectedPhrase.id)
      setPhrases((prev) => prev.filter((p) => p.id !== selectedPhrase.id))
      setTotalCount((prev) => prev - 1)
      handleCloseModal()
    } catch (err) {
      setError(err instanceof Error ? err.message : '削除に失敗しました')
    } finally {
      setIsDeleting(false)
    }
  }

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>保存した表現を読み込み中...</CardTitle>
          <CardDescription className="text-blue-600">少々お待ちください。</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>保存した表現の取得に失敗しました</CardTitle>
          <CardDescription className="text-red-600">{error}</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => void loadPhrases()}>再読み込み</Button>
        </CardContent>
      </Card>
    )
  }

  if (phrases.length === 0) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>保存した表現がありません</CardTitle>
          <CardDescription className="text-blue-600">
            セッション中に改善例文の「保存」ボタンを押すと、ここに表示されます。
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <>
      <Card className="w-full">
        <CardHeader>
          <CardTitle>保存した表現</CardTitle>
          <CardDescription className="text-blue-600">
            全 {totalCount} 件
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {phrases.map((phrase) => (
            <button
              key={phrase.id}
              type="button"
              onClick={() => handlePhraseClick(phrase)}
              className="w-full rounded-lg border border-blue-100 bg-white/70 p-4 text-left transition hover:border-blue-300 hover:bg-blue-50/50"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">{phrase.phrase}</p>
                  <p className="mt-1 line-clamp-2 text-xs text-blue-600">{phrase.explanation}</p>
                </div>
                {phrase.convertedToReviewId ? (
                  <span className="shrink-0 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                    復習済み
                  </span>
                ) : (
                  <span className="shrink-0 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                    未復習
                  </span>
                )}
              </div>
              <p className="mt-2 text-xs text-blue-400">
                {new Date(phrase.createdAt).toLocaleDateString('ja-JP')}
              </p>
            </button>
          ))}

          <Button variant="ghost" size="sm" onClick={() => void loadPhrases()}>
            リストを再読み込み
          </Button>
        </CardContent>
      </Card>

      {/* 詳細モーダル */}
      <Transition.Root show={isModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={handleCloseModal}>
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
                      保存した表現
                    </Dialog.Title>
                  </div>
                  {selectedPhrase && (
                    <div className="space-y-4 px-6 py-5">
                      {selectedPhrase.originalInput && (
                        <div>
                          <p className="text-xs font-semibold uppercase text-gray-500">
                            元の発話
                          </p>
                          <p className="mt-1 text-sm text-gray-700">
                            {selectedPhrase.originalInput}
                          </p>
                        </div>
                      )}
                      <div>
                        <p className="text-xs font-semibold uppercase text-blue-500">
                          改善例文
                        </p>
                        <p className="mt-1 text-lg font-medium text-blue-900">
                          {selectedPhrase.phrase}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase text-gray-500">
                          フィードバック
                        </p>
                        <p className="mt-1 text-sm text-gray-700">
                          {selectedPhrase.explanation}
                        </p>
                      </div>

                      {!selectedPhrase.convertedToReviewId && (
                        <div className="rounded-lg border border-blue-100 bg-blue-50 p-4">
                          <p className="text-sm font-medium text-blue-900">
                            この表現を復習問題にしますか？
                          </p>
                          <p className="mt-1 text-xs text-blue-600">
                            復習問題に追加すると、翌日から復習一覧に表示されます。
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                  <div className="flex gap-3 border-t border-gray-100 bg-gray-50 px-6 py-4">
                    {selectedPhrase && !selectedPhrase.convertedToReviewId && (
                      <Button
                        onClick={() => void handleConvertToReview()}
                        disabled={isConverting}
                        className="flex-1"
                      >
                        {isConverting ? '変換中...' : '復習問題にする'}
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      onClick={() => void handleDelete()}
                      disabled={isDeleting}
                      className={selectedPhrase?.convertedToReviewId ? 'flex-1' : ''}
                    >
                      {isDeleting ? '削除中...' : '削除'}
                    </Button>
                    <Button variant="ghost" onClick={handleCloseModal}>
                      閉じる
                    </Button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
    </>
  )
}

