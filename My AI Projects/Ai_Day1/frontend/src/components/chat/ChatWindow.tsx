import type { ChatMessage } from '../../types';

interface ChatWindowProps {
  messages: ChatMessage[];
}

export function ChatWindow({ messages }: ChatWindowProps) {
  return (
    <main className="flex-1 overflow-auto p-6">
      {messages.length === 0 ? (
        <p className="text-sm text-gray-500">No messages yet.</p>
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="rounded-md border border-gray-200 p-3 text-sm">
              <p className="font-medium">{message.role}</p>
              <p>{message.content}</p>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
