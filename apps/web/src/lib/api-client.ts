const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface RequestOptions extends RequestInit {
  parseJson?: boolean
}

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
}

function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') {
    return {}
  }

  const token = window.localStorage.getItem('access_token')
  if (!token) {
    return {}
  }

  return {
    Authorization: `Bearer ${token}`,
  }
}

export async function apiRequest<T>(
  path: string,
  method: HttpMethod = 'GET',
  body?: unknown,
  options?: RequestOptions,
): Promise<T> {
  const shouldParseJson = options?.parseJson ?? true

  // FormDataの場合はContent-Typeを設定しない（ブラウザが自動設定）
  const isFormData = body instanceof FormData
  const headers = isFormData 
    ? { ...getAuthHeaders(), ...options?.headers }
    : { ...DEFAULT_HEADERS, ...getAuthHeaders(), ...options?.headers }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    body: isFormData ? body : (body ? JSON.stringify(body) : undefined),
    headers,
    ...options,
  })

  if (!response.ok) {
    // 認証エラーの場合
    if (response.status === 401) {
      // トークンをクリアしてログインページにリダイレクト
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
      throw new Error('認証が必要です。ログインしてください。')
    }

    // その他のエラー
    const errorText = await response.text()
    let errorMessage = 'API request failed'
    
    try {
      const errorData = JSON.parse(errorText)
      errorMessage = errorData.detail || errorData.message || errorText
    } catch {
      errorMessage = errorText || errorMessage
    }
    
    throw new Error(errorMessage)
  }

  if (!shouldParseJson) {
    return undefined as T
  }

  return (await response.json()) as T
}


