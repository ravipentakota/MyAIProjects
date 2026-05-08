/** Chat page with thread list, message list, and input interactions. */
import { useEffect, useMemo, useState } from 'react';

import { ChatInput } from '../components/chat/ChatInput';
import { ChatWindow } from '../components/chat/ChatWindow';
import { ThreadSidebar } from '../components/chat/ThreadSidebar';
import { useAuth } from '../hooks/useAuth';
import { attachmentService } from '../services/attachmentService';
import { chatThreadService } from '../services/chatThreadService';
import type { ChatMessage, ChatThread, ConversationTurn } from '../types';

export function ChatPage() {
  const { user, clearSession } = useAuth();
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messagesByThread, setMessagesByThread] = useState<Record<string, ChatMessage[]>>({});
  const [isSending, setIsSending] = useState(false);

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === activeThreadId) ?? null,
    [threads, activeThreadId],
  );

  const activeMessages = useMemo(
    () => (activeThreadId ? messagesByThread[activeThreadId] ?? [] : []),
    [activeThreadId, messagesByThread],
  );

  useEffect(() => {
    if (!user) return;
    chatThreadService
      .listThreads(user.id)
      .then((items) => {
        setThreads(items);
        if (items.length > 0) setActiveThreadId(items[0].id);
      })
      .catch(() => {
        setThreads([]);
      });
  }, [user]);

  useEffect(() => {
    if (!activeThreadId) {
      return;
    }
    chatThreadService
      .listMessages(activeThreadId)
      .then((items) =>
        setMessagesByThread((prev) => ({
          ...prev,
          [activeThreadId]: items,
        })),
      )
      .catch(() =>
        setMessagesByThread((prev) => ({
          ...prev,
          [activeThreadId]: [],
        })),
      );
  }, [activeThreadId]);

  async function handleCreateThread() {
    if (!user) return;
    const created = await chatThreadService.createThread(user.id);
    setThreads((prev) => [created, ...prev]);
    setActiveThreadId(created.id);
    setMessagesByThread((prev) => ({ ...prev, [created.id]: [] }));
  }

  async function ensureThread(): Promise<string | null> {
    if (activeThreadId) return activeThreadId;
    if (!user) return null;
    const created = await chatThreadService.createThread(user.id);
    setThreads((prev) => [created, ...prev]);
    setActiveThreadId(created.id);
    setMessagesByThread((prev) => ({ ...prev, [created.id]: [] }));
    return created.id;
  }

  async function handleSend(content: string, attachmentIds: string[]) {
    const threadId = await ensureThread();
    if (!threadId) return;

    setIsSending(true);
    try {
      const threadMessages = messagesByThread[threadId] ?? [];
      const history: ConversationTurn[] = threadMessages
        .slice(-10)
        .map((item) => ({ role: item.role, content: item.content }));

      const nextMessages = await chatThreadService.sendMessage(
        threadId,
        content,
        user?.email,
        history,
        attachmentIds,
      );
      setMessagesByThread((prev) => ({
        ...prev,
        [threadId as string]: nextMessages,
      }));

      if (user) {
        const refreshed = await chatThreadService.listThreads(user.id);
        setThreads(refreshed);
      }
    } finally {
      setIsSending(false);
    }
  }

  async function handleRenameThread(threadId: string, nextTitle: string) {
    if (!user) return;

    const updated = await chatThreadService.updateThread(user.id, threadId, nextTitle);
    setThreads((prev) => prev.map((thread) => (thread.id === threadId ? updated : thread)));
  }

  return (
    <div className="flex h-screen bg-white text-gray-900">
      <ThreadSidebar
        threads={threads}
        onCreateThread={handleCreateThread}
        activeThreadId={activeThreadId}
        onSelectThread={setActiveThreadId}
        onRenameThread={handleRenameThread}
      />

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-gray-200 px-6 py-3">
          <h1 className="text-base font-semibold">{activeThread?.title || 'Chat Window'}</h1>
          <button
            type="button"
            onClick={clearSession}
            className="rounded-md border border-gray-300 px-3 py-1 text-sm"
          >
            Sign out
          </button>
        </header>
        <ChatWindow messages={activeMessages} />
        <ChatInput
          activeThreadId={activeThreadId}
          onEnsureThread={ensureThread}
          onSend={handleSend}
          onUploadAttachment={attachmentService.uploadAttachment}
          onDeleteAttachment={attachmentService.deleteAttachment}
          disabled={isSending}
        />
      </div>
    </div>
  );
}
