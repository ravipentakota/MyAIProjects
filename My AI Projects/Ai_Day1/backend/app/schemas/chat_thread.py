"""Chat thread schema placeholders."""
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.attachment import AttachmentResponse


class ChatThreadCreate(BaseModel):
    """Create-thread request schema."""

    title: Optional[str] = None


class ChatThreadUpdate(BaseModel):
    """Update-thread request schema."""

    title: Optional[str] = None


class ChatThreadResponse(BaseModel):
    """Thread response schema placeholder."""

    id: str
    user_id: str
    title: str
    created_at: str


class ConversationTurn(BaseModel):
    """Single conversational turn passed as context."""

    role: str
    content: str


class ChatMessageCreate(BaseModel):
    """Create-message request schema."""

    content: str
    history: list[ConversationTurn] | None = None
    attachment_ids: list[str] | None = None


class ChatMessageResponse(BaseModel):
    """Message response schema."""

    id: str
    thread_id: str
    role: str
    content: str
    created_at: str
    attachments: list[AttachmentResponse] = Field(default_factory=list)
