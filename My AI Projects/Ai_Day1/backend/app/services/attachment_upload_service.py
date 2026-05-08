"""Attachment upload and metadata service."""
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chat_attachment import ChatAttachment
from app.models.chat_thread import ChatThread
from app.schemas.attachment import AttachmentDeleteResponse, AttachmentResponse
from app.services.attachment_ai_service import attachment_ai_service
from app.services.attachment_storage_service import LocalAttachmentStorage

_ATTACHMENT_TYPE_BY_EXTENSION: dict[str, str] = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".webp": "image",
    ".mp4": "video",
    ".webm": "video",
    ".mov": "video",
    ".csv": "table",
    ".tsv": "table",
    ".xlsx": "table",
    ".xls": "table",
    ".pdf": "document",
    ".txt": "document",
    ".doc": "document",
    ".docx": "document",
    ".rtf": "document",
    ".ppt": "document",
    ".pptx": "document",
    ".tex": "formula",
    ".latex": "formula",
    ".math": "formula",
    ".py": "code",
    ".ts": "code",
    ".tsx": "code",
    ".js": "code",
    ".jsx": "code",
    ".json": "code",
    ".sql": "code",
    ".html": "code",
    ".css": "code",
    ".java": "code",
    ".cpp": "code",
    ".c": "code",
    ".cs": "code",
}

_MIME_PREFIX_FALLBACK = {
    "image/": "image",
    "video/": "video",
    "text/": "code",
}


class AttachmentUploadService:
    """Attachment CRUD and validation orchestration."""

    def __init__(self) -> None:
        self.storage = LocalAttachmentStorage(settings.UPLOAD_DIR)
        self.max_size_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

    @staticmethod
    def to_attachment_response(attachment: ChatAttachment) -> AttachmentResponse:
        return AttachmentResponse(
            id=attachment.id,
            thread_id=attachment.thread_id,
            message_id=attachment.message_id,
            filename=attachment.filename,
            mime_type=attachment.mime_type,
            size_bytes=attachment.size_bytes,
            attachment_type=attachment.attachment_type,
            created_at=attachment.created_at.isoformat(),
            content_url=f"/api/attachments/{attachment.id}/content",
        )

    def _detect_attachment_type(self, filename: str, mime_type: str | None) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix in _ATTACHMENT_TYPE_BY_EXTENSION:
            return _ATTACHMENT_TYPE_BY_EXTENSION[suffix]

        for prefix, attachment_type in _MIME_PREFIX_FALLBACK.items():
            if (mime_type or "").startswith(prefix):
                return attachment_type

        # Keep validation strict for unknown empty uploads, but allow broader document uploads
        # for business files (pdf/doc/etc.) and future AI processing pipelines.
        if mime_type and mime_type != "application/octet-stream":
            return "document"
        if suffix:
            return "document"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "unsupported_attachment_type", "message": "Unsupported attachment type."},
        )

    async def upload_attachment(
        self,
        db: AsyncSession,
        thread_id: str,
        upload: UploadFile,
    ) -> AttachmentResponse:
        """Validate, persist, and return attachment metadata."""
        thread = await db.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "thread_not_found", "message": "Thread not found."},
            )

        filename = upload.filename or "attachment"
        attachment_type = self._detect_attachment_type(filename, upload.content_type)
        stored_name, size_bytes = await self.storage.save(upload)

        if size_bytes > self.max_size_bytes:
            self.storage.delete(stored_name)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": "attachment_too_large",
                    "message": f"Attachment exceeds the {settings.MAX_UPLOAD_MB} MB limit.",
                },
            )

        attachment = ChatAttachment(
            thread_id=thread_id,
            filename=filename,
            stored_name=stored_name,
            mime_type=upload.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            attachment_type=attachment_type,
        )
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)

        response = self.to_attachment_response(attachment)
        await attachment_ai_service.schedule_processing(response)
        return response

    async def list_thread_attachments(self, db: AsyncSession, thread_id: str) -> list[AttachmentResponse]:
        """Return attachment history for a thread."""
        rows = await db.scalars(
            select(ChatAttachment)
            .where(ChatAttachment.thread_id == thread_id)
            .order_by(ChatAttachment.created_at.asc())
        )
        return [self.to_attachment_response(item) for item in rows.all()]

    async def get_attachment(self, db: AsyncSession, attachment_id: str) -> ChatAttachment:
        attachment = await db.scalar(select(ChatAttachment).where(ChatAttachment.id == attachment_id))
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "attachment_not_found", "message": "Attachment not found."},
            )
        return attachment

    async def get_attachment_content(self, db: AsyncSession, attachment_id: str) -> FileResponse:
        attachment = await self.get_attachment(db=db, attachment_id=attachment_id)
        path = self.storage.resolve_path(attachment.stored_name)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "attachment_missing", "message": "Attachment file is missing."},
            )
        return FileResponse(path=path, media_type=attachment.mime_type, filename=attachment.filename)

    async def delete_attachment(self, db: AsyncSession, attachment_id: str) -> AttachmentDeleteResponse:
        attachment = await self.get_attachment(db=db, attachment_id=attachment_id)
        self.storage.delete(attachment.stored_name)
        await db.delete(attachment)
        await db.commit()
        return AttachmentDeleteResponse(id=attachment_id, deleted=True)

    async def attach_to_message(self, db: AsyncSession, thread_id: str, message_id: str, attachment_ids: list[str]) -> None:
        """Associate uploaded thread attachments with a concrete message."""
        if not attachment_ids:
            return

        rows = await db.scalars(
            select(ChatAttachment).where(
                ChatAttachment.id.in_(attachment_ids),
                ChatAttachment.thread_id == thread_id,
            )
        )
        for attachment in rows.all():
            attachment.message_id = message_id

    async def list_message_attachments(self, db: AsyncSession, message_id: str) -> list[AttachmentResponse]:
        rows = await db.scalars(
            select(ChatAttachment)
            .where(ChatAttachment.message_id == message_id)
            .order_by(ChatAttachment.created_at.asc())
        )
        return [self.to_attachment_response(item) for item in rows.all()]


attachment_upload_service = AttachmentUploadService()
