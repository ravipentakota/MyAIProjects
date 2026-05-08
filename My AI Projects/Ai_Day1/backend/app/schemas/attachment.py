"""Attachment request and response schemas."""
from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    """Attachment metadata returned to the frontend."""

    id: str
    thread_id: str
    message_id: str | None
    filename: str
    mime_type: str
    size_bytes: int
    attachment_type: str
    created_at: str
    content_url: str


class AttachmentDeleteResponse(BaseModel):
    """Attachment deletion confirmation."""

    id: str
    deleted: bool
