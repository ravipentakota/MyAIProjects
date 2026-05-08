import type { PendingAttachment } from '../../types';

interface PendingAttachmentListProps {
  attachments: PendingAttachment[];
  disabled?: boolean;
  onRemove: (clientId: string) => void;
}

export function PendingAttachmentList({ attachments, disabled = false, onRemove }: PendingAttachmentListProps) {
  if (attachments.length === 0) return null;

  return (
    <div className="mb-3 grid gap-2 sm:grid-cols-2">
      {attachments.map((attachment) => (
        <div key={attachment.clientId} className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="truncate font-medium text-gray-900">{attachment.file.name}</div>
              <div className="text-xs text-gray-500">{attachment.status}</div>
            </div>
            <button
              type="button"
              onClick={() => onRemove(attachment.clientId)}
              disabled={disabled}
              className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600"
            >
              Remove
            </button>
          </div>
          <div className="mt-2 h-2 rounded-full bg-gray-200">
            <div
              className={`h-2 rounded-full ${attachment.status === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}
              style={{ width: `${attachment.progress}%` }}
            />
          </div>
          {attachment.errorMessage ? <div className="mt-2 text-xs text-red-600">{attachment.errorMessage}</div> : null}
        </div>
      ))}
    </div>
  );
}
