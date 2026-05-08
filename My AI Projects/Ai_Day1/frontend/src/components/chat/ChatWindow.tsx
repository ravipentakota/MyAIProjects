import { MessageAttachment } from '../attachments/MessageAttachment';

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
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-xs rounded-lg p-3 text-sm ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-900'
                }`}
              >
                {message.content ? <p className="text-justify">{message.content}</p> : null}
                {message.attachments.length > 0 ? (
                  <div className={`${message.content ? 'mt-3' : ''} space-y-3`}>
                    {message.attachments.map((attachment) => (
                      <MessageAttachment key={attachment.id} attachment={attachment} />
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

