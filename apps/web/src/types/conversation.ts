export interface ConversationTurn {
  id: string
  roundIndex: number
  userMessage: string
  aiReply: {
    message: string
    feedbackShort: string
    improvedSentence: string
    tags: string[]
    scores: {
      pronunciation: number | null
      grammar: number | null
    } | null
    details: {
      explanation?: string | null
      suggestions?: string[] | null
    } | null
    createdAt: string
  }
  createdAt: string
  isPending?: boolean
  shouldEndSession?: boolean
}

export interface SessionStatus {
  sessionId: number
  scenarioId: number
  scenarioName?: string
  roundTarget: number
  completedRounds: number
  difficulty: string
  difficultyLabel?: string
  mode: string
  modeLabel?: string
  isActive: boolean
  canExtend: boolean
  extensionOffered: boolean
}

export interface SessionSummary {
  sessionId: number
  completedRounds: number
  topPhrases: Array<{
    phrase: string
    explanation: string
    roundIndex?: number
  }>
  nextReviewAt?: string
  scenarioName?: string
  difficulty?: string
  mode?: string
}


