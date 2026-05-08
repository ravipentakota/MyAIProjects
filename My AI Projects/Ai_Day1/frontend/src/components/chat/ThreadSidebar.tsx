import { useState } from 'react';

import type { ChatThread } from '../../types';

interface ThreadSidebarProps {
  threads: ChatThread[];
  onCreateThread: () => void;
  activeThreadId: string | null;
  onSelectThread: (threadId: string) => void;
  onRenameThread: (threadId: string, nextTitle: string) => Promise<void> | void;
}

export function ThreadSidebar({
  threads,
  onCreateThread,
  activeThreadId,
  onSelectThread,
  onRenameThread,
}: ThreadSidebarProps) {
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState('');

  function startRenaming(thread: ChatThread) {
    setEditingThreadId(thread.id);
    setDraftTitle(thread.title || 'Untitled');
  }

  async function commitRename(threadId: string, currentTitle: string) {
    const trimmed = draftTitle.trim();
    setEditingThreadId(null);

    if (!trimmed || trimmed === currentTitle) {
      setDraftTitle('');
      return;
    }

    await onRenameThread(threadId, trimmed);
    setDraftTitle('');
  }

  function cancelRename() {
    setEditingThreadId(null);
    setDraftTitle('');
  }

  return (
    <aside className="w-72 border-r border-gray-200 p-4">
      <button
        type="button"
        className="w-full rounded-md bg-blue-600 px-3 py-2 text-sm text-white"
        onClick={onCreateThread}
      >
        New Thread
      </button>
      <div className="mt-4 space-y-2">
        {threads.map((thread) => (
          <div
            key={thread.id}
            className={`flex items-center gap-2 rounded-md border px-2 py-2 ${
              activeThreadId === thread.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
            }`}
          >
            {editingThreadId === thread.id ? (
              <input
                autoFocus
                value={draftTitle}
                onChange={(event) => setDraftTitle(event.target.value)}
                onBlur={() => {
                  void commitRename(thread.id, thread.title || 'Untitled');
                }}
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    void commitRename(thread.id, thread.title || 'Untitled');
                  }
                  if (event.key === 'Escape') {
                    event.preventDefault();
                    cancelRename();
                  }
                }}
                className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
              />
            ) : (
              <button
                type="button"
                className="flex-1 truncate text-left text-sm"
                onClick={() => onSelectThread(thread.id)}
                onDoubleClick={() => startRenaming(thread)}
              >
                {thread.title || 'Untitled'}
              </button>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
}
