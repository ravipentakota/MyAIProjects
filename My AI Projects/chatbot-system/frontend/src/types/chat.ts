export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  createdAt?: string
}

export interface APIResponse {
  success: boolean
  message?: string
}

export interface ChatRequest {
  message: string
}

export interface ChatReply {
  reply: string
}
