export interface User {
  id: string;
  email: string;
  fullName?: string;
}

export interface ChatThread {
  id: string;
  title: string;
  createdAt: string;
}

export interface ChatMessage {
  id: string;
  threadId: string;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}
