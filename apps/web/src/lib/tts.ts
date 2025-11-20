const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

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

export async function playTextWithTts(text: string, voiceProfile?: string): Promise<void> {
  if (!text.trim()) return

  const response = await fetch(`${API_BASE_URL}/audio/tts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({
      text,
      voice_profile: voiceProfile,
    }),
  })

  if (!response.ok) {
    const msg = await response.text()
    throw new Error(msg || '音声の取得に失敗しました')
  }

  const blob = await response.blob()
  const url = URL.createObjectURL(blob)

  try {
    const audio = new Audio(url)
    await audio.play()
  } finally {
    URL.revokeObjectURL(url)
  }
}


