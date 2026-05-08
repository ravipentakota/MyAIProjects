import type { ChatThread } from '../types';
import type { ChatAttachment } from '../types';
import type { ChatMessage } from '../types';
import type { ConversationTurn } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';

function headers(userId: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'x-user-id': userId,
  };
}

function mapAttachment(item: {
  id: string;
  thread_id: string;
  message_id: string | null;
  filename: string;
  mime_type: string;
  size_bytes: number;
  attachment_type: 'image' | 'video' | 'table' | 'formula' | 'code' | 'document';
  created_at: string;
  content_url: string;
}): ChatAttachment {
  return {
    id: item.id,
    threadId: item.thread_id,
    messageId: item.message_id,
    filename: item.filename,
    mimeType: item.mime_type,
    sizeBytes: item.size_bytes,
    attachmentType: item.attachment_type,
    createdAt: item.created_at,
    contentUrl: item.content_url.startsWith('http') ? item.content_url : `${API_BASE_URL}${item.content_url}`,
  };
}

export const chatThreadService = {
  async listThreads(userId: string): Promise<ChatThread[]> {
    const response = await fetch(`${API_BASE_URL}/api/threads`, {
      method: 'GET',
      headers: headers(userId),
    });
    if (!response.ok) throw new Error('Failed to load threads');
    const data = (await response.json()) as Array<{
      id: string;
      title: string;
      created_at: string;
    }>;
    return data.map((item) => ({
      id: item.id,
      title: item.title,
      createdAt: item.created_at,
    }));
  },

  async createThread(userId: string, title?: string): Promise<ChatThread> {
    const response = await fetch(`${API_BASE_URL}/api/threads`, {
      method: 'POST',
      headers: headers(userId),
      body: JSON.stringify({ title: title ?? null }),
    });
    if (!response.ok) throw new Error('Failed to create thread');
    const item = (await response.json()) as { id: string; title: string; created_at: string };
    return { id: item.id, title: item.title, createdAt: item.created_at };
  },

  async updateThread(userId: string, threadId: string, title: string): Promise<ChatThread> {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
      method: 'PATCH',
      headers: headers(userId),
      body: JSON.stringify({ title }),
    });
    if (!response.ok) throw new Error('Failed to update thread');
    const item = (await response.json()) as { id: string; title: string; created_at: string };
    return { id: item.id, title: item.title, createdAt: item.created_at };
  },

  async deleteThread(userId: string, threadId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
      method: 'DELETE',
      headers: headers(userId),
    });
    if (!response.ok) throw new Error('Failed to delete thread');
  },

  async listMessages(threadId: string): Promise<ChatMessage[]> {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/messages`, {
      method: 'GET',
    });
    if (!response.ok) throw new Error('Failed to load messages');
    const data = (await response.json()) as Array<{
      id: string;
      thread_id: string;
      role: 'user' | 'assistant';
      content: string;
      created_at: string;
      attachments?: Array<{
        id: string;
        thread_id: string;
        message_id: string | null;
        filename: string;
        mime_type: string;
        size_bytes: number;
        attachment_type: 'image' | 'video' | 'table' | 'formula' | 'code' | 'document';
        created_at: string;
        content_url: string;
      }>;
    }>;
    return data
      .map((item) => ({
      id: item.id,
      threadId: item.thread_id,
      role: item.role,
      content: item.content,
      createdAt: item.created_at,
      attachments: (item.attachments ?? []).map(mapAttachment),
      }))
      .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  },

  async sendMessage(
    threadId: string,
    content: string,
    userEmail?: string,
    history: ConversationTurn[] = [],
    attachmentIds: string[] = [],
  ): Promise<ChatMessage[]> {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(userEmail ? { 'x-user-email': userEmail } : {}),
      },
      body: JSON.stringify({ content, history, attachment_ids: attachmentIds }),
    });
    if (!response.ok) throw new Error('Failed to send message');
    const data = (await response.json()) as Array<{
      id: string;
      thread_id: string;
      role: 'user' | 'assistant';
      content: string;
      created_at: string;
      attachments?: Array<{
        id: string;
        thread_id: string;
        message_id: string | null;
        filename: string;
        mime_type: string;
        size_bytes: number;
        attachment_type: 'image' | 'video' | 'table' | 'formula' | 'code' | 'document';
        created_at: string;
        content_url: string;
      }>;
    }>;
    return data
      .map((item) => ({
      id: item.id,
      threadId: item.thread_id,
      role: item.role,
      content: item.content,
      createdAt: item.created_at,
      attachments: (item.attachments ?? []).map(mapAttachment),
      }))
      .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  },
};
