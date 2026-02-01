import { apiRequest } from '@/lib/api-client'
import type {
  CustomScenario,
  CustomScenarioCreate,
  CustomScenarioListResponse,
  CustomScenarioLimitResponse,
} from '@/types/scenario'

/**
 * カスタムシナリオの作成可能数を取得
 */
export async function fetchCustomScenarioLimit(): Promise<CustomScenarioLimitResponse> {
  return apiRequest<CustomScenarioLimitResponse>('/custom-scenarios/limit', 'GET')
}

/**
 * カスタムシナリオ一覧を取得
 */
export async function fetchCustomScenarios(
  limit = 50,
  offset = 0
): Promise<CustomScenarioListResponse> {
  return apiRequest<CustomScenarioListResponse>(
    `/custom-scenarios?limit=${limit}&offset=${offset}`,
    'GET'
  )
}

/**
 * カスタムシナリオを作成
 */
export async function createCustomScenario(
  data: CustomScenarioCreate
): Promise<CustomScenario> {
  return apiRequest<CustomScenario>('/custom-scenarios', 'POST', data)
}

/**
 * カスタムシナリオを取得
 */
export async function fetchCustomScenario(id: number): Promise<CustomScenario> {
  return apiRequest<CustomScenario>(`/custom-scenarios/${id}`, 'GET')
}

/**
 * カスタムシナリオを削除
 */
export async function deleteCustomScenario(id: number): Promise<void> {
  await apiRequest(`/custom-scenarios/${id}`, 'DELETE')
}
