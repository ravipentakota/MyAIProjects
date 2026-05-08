import type { ChatMessage } from "../../types";

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
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-900"
                }`}
              >
                <p className="text-justify">{message.content}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

