import { useEffect, useState } from 'react';

import type { ChatAttachment } from '../../types';

interface MessageAttachmentProps {
  attachment: ChatAttachment;
}

function parseDelimitedTable(content: string): string[][] {
  const lines = content.trim().split(/\r?\n/).filter(Boolean);
  const separator = lines[0]?.includes('\t') ? '\t' : ',';
  return lines.slice(0, 6).map((line) => line.split(separator).map((cell) => cell.trim()));
}

export function MessageAttachment({ attachment }: MessageAttachmentProps) {
  const [textContent, setTextContent] = useState<string>('');

  useEffect(() => {
    if (!['code', 'formula', 'table'].includes(attachment.attachmentType)) return;
    if (!attachment.mimeType.startsWith('text/') && !attachment.filename.match(/\.(csv|tsv|tex|py|ts|tsx|js|jsx|json|sql|html|css|java|cpp|c|cs)$/i)) {
      return;
    }

    fetch(attachment.contentUrl)
      .then((response) => response.text())
      .then((value) => setTextContent(value))
      .catch(() => setTextContent(''));
  }, [attachment]);

  if (attachment.attachmentType === 'image') {
    return <img src={attachment.contentUrl} alt={attachment.filename} className="max-h-64 rounded-lg object-cover" />;
  }

  if (attachment.attachmentType === 'video') {
    return <video src={attachment.contentUrl} controls className="max-h-72 rounded-lg" />;
  }

  if (attachment.attachmentType === 'table' && textContent) {
    const rows = parseDelimitedTable(textContent);
    return (
      <div className="overflow-auto rounded-lg border border-gray-300 bg-white p-2 text-xs text-gray-900">
        <div className="mb-2 font-medium">{attachment.filename}</div>
        <table className="min-w-full border-collapse">
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={`${attachment.id}-${rowIndex}`}>
                {row.map((cell, cellIndex) => (
                  <td key={`${attachment.id}-${rowIndex}-${cellIndex}`} className="border border-gray-200 px-2 py-1">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (attachment.attachmentType === 'formula') {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-gray-900">
        <div className="mb-1 font-medium">{attachment.filename}</div>
        <pre className="whitespace-pre-wrap font-mono text-xs">{textContent || 'Formula document uploaded.'}</pre>
      </div>
    );
  }

  if (attachment.attachmentType === 'code') {
    return (
      <div className="rounded-lg border border-gray-300 bg-gray-950 p-3 text-xs text-gray-100">
        <div className="mb-2 text-sm font-medium text-gray-300">{attachment.filename}</div>
        <pre className="overflow-auto whitespace-pre-wrap font-mono">{textContent || 'Code file uploaded.'}</pre>
      </div>
    );
  }

  return (
    <a
      href={attachment.contentUrl}
      target="_blank"
      rel="noreferrer"
      className="inline-flex rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-blue-700"
    >
      {attachment.filename}
    </a>
  );
}
