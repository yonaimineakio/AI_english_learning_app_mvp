"use client"

import { Fragment, useState, useEffect } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { PlusIcon, SparklesIcon } from '@heroicons/react/24/outline'

import { createCustomScenario, fetchCustomScenarioLimit } from '@/lib/custom-scenarios'
import type { CustomScenarioCreate } from '@/types/scenario'

interface CreateCustomScenarioDialogProps {
  open: boolean
  onClose: () => void
  onSuccess?: () => void
}

export function CreateCustomScenarioDialog({
  open,
  onClose,
  onSuccess,
}: CreateCustomScenarioDialogProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<CustomScenarioCreate>({
    name: '',
    description: '',
    user_role: '',
    ai_role: '',
  })
  const [error, setError] = useState<string | null>(null)

  // 作成制限を取得
  const { data: limitData, refetch: refetchLimit } = useQuery({
    queryKey: ['customScenarioLimit'],
    queryFn: fetchCustomScenarioLimit,
    enabled: open,
  })

  // ダイアログを開くたびに制限を更新
  useEffect(() => {
    if (open) {
      refetchLimit()
    }
  }, [open, refetchLimit])

  // 作成ミューテーション
  const createMutation = useMutation({
    mutationFn: createCustomScenario,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customScenarios'] })
      queryClient.invalidateQueries({ queryKey: ['customScenarioLimit'] })
      setFormData({ name: '', description: '', user_role: '', ai_role: '' })
      setError(null)
      onSuccess?.()
      onClose()
    },
    onError: (err: Error) => {
      setError(err.message || 'シナリオの作成に失敗しました')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // バリデーション
    if (!formData.name.trim()) {
      setError('シナリオ名を入力してください')
      return
    }
    if (!formData.user_role.trim()) {
      setError('あなたの役割を入力してください')
      return
    }
    if (!formData.ai_role.trim()) {
      setError('AIの役割を入力してください')
      return
    }
    if (!formData.description.trim()) {
      setError('シナリオの説明を入力してください')
      return
    }

    createMutation.mutate(formData)
  }

  const canCreate = limitData ? limitData.remaining > 0 : false

  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-900/30 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center sm:p-6">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative w-full max-w-lg transform overflow-hidden rounded-2xl bg-white text-left shadow-xl transition-all">
                <form onSubmit={handleSubmit}>
                  <div className="border-b border-gray-100 px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
                        <SparklesIcon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <Dialog.Title className="text-xl font-semibold text-gray-900">
                          オリジナルシナリオを作成
                        </Dialog.Title>
                        <p className="text-sm text-gray-500">
                          あなただけの学習シナリオを作成しましょう
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-5 px-6 py-5">
                    {/* 制限表示 */}
                    {limitData && (
                      <div className="rounded-lg bg-blue-50 px-4 py-3 text-sm">
                        <span className="text-blue-700">
                          本日の作成可能数:{' '}
                          <span className="font-semibold">{limitData.remaining}</span> /{' '}
                          {limitData.daily_limit}
                        </span>
                        {!limitData.is_pro && limitData.remaining === 0 && (
                          <p className="mt-1 text-xs text-blue-600">
                            Proプランにアップグレードすると、1日5個まで作成できます
                          </p>
                        )}
                      </div>
                    )}

                    {/* シナリオ名 */}
                    <div>
                      <label
                        htmlFor="name"
                        className="mb-1.5 block text-sm font-medium text-gray-700"
                      >
                        シナリオ名
                      </label>
                      <input
                        type="text"
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="例: カフェで注文する"
                        className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        disabled={!canCreate || createMutation.isPending}
                      />
                    </div>

                    {/* あなたの役割 */}
                    <div>
                      <label
                        htmlFor="user_role"
                        className="mb-1.5 block text-sm font-medium text-gray-700"
                      >
                        あなたの役割
                      </label>
                      <input
                        type="text"
                        id="user_role"
                        value={formData.user_role}
                        onChange={(e) => setFormData({ ...formData, user_role: e.target.value })}
                        placeholder="例: カフェに来た客"
                        className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        disabled={!canCreate || createMutation.isPending}
                      />
                    </div>

                    {/* AIの役割 */}
                    <div>
                      <label
                        htmlFor="ai_role"
                        className="mb-1.5 block text-sm font-medium text-gray-700"
                      >
                        AIの役割
                      </label>
                      <input
                        type="text"
                        id="ai_role"
                        value={formData.ai_role}
                        onChange={(e) => setFormData({ ...formData, ai_role: e.target.value })}
                        placeholder="例: カフェの店員"
                        className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        disabled={!canCreate || createMutation.isPending}
                      />
                    </div>

                    {/* シナリオの説明 */}
                    <div>
                      <label
                        htmlFor="description"
                        className="mb-1.5 block text-sm font-medium text-gray-700"
                      >
                        シナリオの説明
                      </label>
                      <textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="例: あなたはカフェに入り、コーヒーを注文しようとしています。店員に希望を伝えて注文を完了させましょう。"
                        rows={3}
                        className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        disabled={!canCreate || createMutation.isPending}
                      />
                    </div>

                    {/* エラー表示 */}
                    {error && (
                      <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                        {error}
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3 border-t border-gray-100 bg-gray-50 px-6 py-4">
                    <button
                      type="button"
                      onClick={onClose}
                      className="flex-1 rounded-lg border border-gray-300 bg-white py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
                      disabled={createMutation.isPending}
                    >
                      キャンセル
                    </button>
                    <button
                      type="submit"
                      disabled={!canCreate || createMutation.isPending}
                      className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {createMutation.isPending ? (
                        <>
                          <svg
                            className="h-4 w-4 animate-spin"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              className="opacity-25"
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="currentColor"
                              strokeWidth="4"
                            />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                          作成中...
                        </>
                      ) : (
                        <>
                          <PlusIcon className="h-4 w-4" />
                          作成する
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}
