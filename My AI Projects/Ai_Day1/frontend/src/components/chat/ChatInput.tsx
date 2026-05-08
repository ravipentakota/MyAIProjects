import { useRef, useState, type DragEvent, type FormEvent } from 'react';

import { PendingAttachmentList } from '../attachments/PendingAttachmentList';
import type { ChatAttachment, PendingAttachment } from '../../types';

interface ChatInputProps {
  activeThreadId: string | null;
  onEnsureThread: () => Promise<string | null>;
  onSend: (content: string, attachmentIds: string[]) => Promise<void> | void;
  onUploadAttachment: (
    threadId: string,
    file: File,
    onProgress: (progress: number) => void,
  ) => Promise<ChatAttachment>;
  onDeleteAttachment: (attachmentId: string) => Promise<void>;
  disabled?: boolean;
}

export function ChatInput({
  activeThreadId,
  onEnsureThread,
  onSend,
  onUploadAttachment,
  onDeleteAttachment,
  disabled = false,
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const [pendingAttachments, setPendingAttachments] = useState<PendingAttachment[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function uploadFiles(files: FileList | File[]) {
    const fileArray = Array.from(files);
    if (fileArray.length === 0) return;

    const threadId = activeThreadId || (await onEnsureThread());
    if (!threadId) return;

    for (const file of fileArray) {
      const clientId = `${file.name}-${file.size}-${Date.now()}-${Math.random()}`;
      setPendingAttachments((prev) => [
        ...prev,
        { clientId, file, progress: 0, status: 'queued' },
      ]);

      try {
        setPendingAttachments((prev) =>
          prev.map((item) =>
            item.clientId === clientId ? { ...item, status: 'uploading', progress: 5 } : item,
          ),
        );

        const uploaded = await onUploadAttachment(threadId, file, (progress) => {
          setPendingAttachments((prev) =>
            prev.map((item) => (item.clientId === clientId ? { ...item, progress, status: 'uploading' } : item)),
          );
        });

        setPendingAttachments((prev) =>
          prev.map((item) =>
            item.clientId === clientId
              ? { ...item, progress: 100, status: 'uploaded', uploadedAttachmentId: uploaded.id }
              : item,
          ),
        );
      } catch (error) {
        setPendingAttachments((prev) =>
          prev.map((item) =>
            item.clientId === clientId
              ? {
                  ...item,
                  status: 'error',
                  errorMessage: error instanceof Error ? error.message : 'Upload failed',
                }
              : item,
          ),
        );
      }
    }
  }

  async function handleRemoveAttachment(clientId: string) {
    const attachment = pendingAttachments.find((item) => item.clientId === clientId);
    if (attachment?.uploadedAttachmentId) {
      await onDeleteAttachment(attachment.uploadedAttachmentId);
    }
    setPendingAttachments((prev) => prev.filter((item) => item.clientId !== clientId));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const content = value.trim();
    const attachmentIds = pendingAttachments
      .filter((item) => item.status === 'uploaded' && item.uploadedAttachmentId)
      .map((item) => item.uploadedAttachmentId as string);

    if ((!content && attachmentIds.length === 0) || disabled) return;
    setValue('');
    await onSend(content, attachmentIds);
    setPendingAttachments([]);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    void uploadFiles(event.dataTransfer.files);
  }

  return (
    <div
      className={`border-t border-gray-200 p-4 ${dragActive ? 'bg-blue-50' : ''}`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
    >
      <PendingAttachmentList attachments={pendingAttachments} onRemove={(id) => void handleRemoveAttachment(id)} />
      <form onSubmit={handleSubmit}>
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="rounded-md border border-gray-300 px-3 py-2 text-sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
          >
            Attach
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={(event) => {
              if (!event.target.files) return;
              void uploadFiles(event.target.files);
              event.target.value = '';
            }}
          />
          <input
            type="text"
            placeholder="Type a message or drop files here..."
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            disabled={disabled}
          />
        </div>
      </form>
    </div>
  );
}
