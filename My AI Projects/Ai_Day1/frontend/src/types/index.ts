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
  attachments: ChatAttachment[];
}

export interface ConversationTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatAttachment {
  id: string;
  threadId: string;
  messageId: string | null;
  filename: string;
  mimeType: string;
  sizeBytes: number;
  attachmentType: 'image' | 'video' | 'table' | 'formula' | 'code' | 'document';
  createdAt: string;
  contentUrl: string;
}

export interface PendingAttachment {
  clientId: string;
  file: File;
  uploadedAttachmentId?: string;
  progress: number;
  status: 'queued' | 'uploading' | 'uploaded' | 'error';
  errorMessage?: string;
}
