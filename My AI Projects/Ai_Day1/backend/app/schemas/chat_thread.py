"""Chat thread schema placeholders."""
from typing import Optional

from pydantic import BaseModel


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


class ChatMessageCreate(BaseModel):
    """Create-message request schema."""

    content: str


class ChatMessageResponse(BaseModel):
    """Message response schema."""

    id: str
    thread_id: str
    role: str
    content: str
    created_at: str
