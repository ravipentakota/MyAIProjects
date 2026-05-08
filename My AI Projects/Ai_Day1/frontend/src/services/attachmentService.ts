import type { ChatAttachment } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8002';

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

export const attachmentService = {
  uploadAttachment(
    threadId: string,
    file: File,
    onProgress?: (progress: number) => void,
  ): Promise<ChatAttachment> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      xhr.open('POST', `${API_BASE_URL}/api/threads/${threadId}/attachments`);

      xhr.upload.onprogress = (event) => {
        if (!event.lengthComputable || !onProgress) return;
        onProgress(Math.round((event.loaded / event.total) * 100));
      };

      xhr.onload = () => {
        if (xhr.status < 200 || xhr.status >= 300) {
          let message = 'Failed to upload attachment';
          try {
            const body = JSON.parse(xhr.responseText) as { detail?: { message?: string } | string };
            if (typeof body.detail === 'string') {
              message = body.detail;
            } else if (body.detail && typeof body.detail === 'object' && body.detail.message) {
              message = body.detail.message;
            }
          } catch {
            if (xhr.responseText) {
              message = `${message} (${xhr.status})`;
            }
          }
          reject(new Error(message));
          return;
        }

        const payload = JSON.parse(xhr.responseText) as Parameters<typeof mapAttachment>[0];
        resolve(mapAttachment(payload));
      };

      xhr.onerror = () => reject(new Error('Network error while uploading attachment'));
      xhr.send(formData);
    });
  },

  async deleteAttachment(attachmentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/attachments/${attachmentId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete attachment');
  },
};
