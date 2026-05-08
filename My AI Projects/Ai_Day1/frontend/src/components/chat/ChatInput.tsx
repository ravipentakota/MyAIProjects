import { useState, type FormEvent } from 'react';

interface ChatInputProps {
  onSend: (content: string) => Promise<void> | void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled = false }: ChatInputProps) {
  const [value, setValue] = useState('');

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const content = value.trim();
    if (!content || disabled) return;
    setValue('');
    await onSend(content);
  }

  return (
    <div className="border-t border-gray-200 p-4">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Type a message..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
        />
      </form>
    </div>
  );
}
