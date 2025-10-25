"use client"

import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'

import { getScenarioDetail } from '@/lib/scenarios'
import { formatMinutes } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

interface ScenarioDetailDialogProps {
  scenarioId?: number
  open: boolean
  onClose: () => void
}

const difficultyColorMap = {
  beginner: 'bg-emerald-50 text-emerald-700',
  intermediate: 'bg-amber-50 text-amber-700',
  advanced: 'bg-purple-50 text-purple-700',
}

const difficultyLabelMap = {
  beginner: '初級',
  intermediate: '中級',
  advanced: '上級',
}

export function ScenarioDetailDialog({ scenarioId, open, onClose }: ScenarioDetailDialogProps) {
  const scenario = scenarioId ? getScenarioDetail(scenarioId) : null

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
                {scenario ? (
                  <>
                    <div className="border-b border-gray-100 px-6 py-6">
                      <div className="flex items-start justify-between">
                        <Dialog.Title className="text-2xl font-semibold text-gray-900">
                          {scenario.name}
                        </Dialog.Title>
                        <Badge className={difficultyColorMap[scenario.difficulty]}>
                          {difficultyLabelMap[scenario.difficulty]}
                        </Badge>
                      </div>
                      <div className="mt-2 text-sm text-gray-500">
                        所要時間目安: {formatMinutes(scenario.estimatedMinutes)}
                      </div>
                      <p className="mt-4 text-gray-600">{scenario.description}</p>
                    </div>

                    <div className="space-y-6 px-6 py-6">
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900">学習ゴール</h3>
                        <ul className="mt-3 list-inside list-disc space-y-2 text-sm text-gray-600">
                          {scenario.learningGoals.map((goal) => (
                            <li key={goal}>{goal}</li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <h3 className="text-sm font-semibold text-gray-900">サンプルフレーズ</h3>
                        <div className="mt-3 rounded-xl bg-blue-50 p-4 text-sm text-blue-900">
                          “{scenario.sampleDialog}”
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-gray-100 bg-gray-50 px-6 py-4">
                      <button
                        type="button"
                        className="w-full rounded-lg border border-gray-200 bg-white py-2 text-sm font-medium text-gray-700 transition hover:border-gray-300"
                        onClick={onClose}
                      >
                        閉じる
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="px-6 py-10 text-center text-gray-500">シナリオが見つかりませんでした。</div>
                )}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  )
}

