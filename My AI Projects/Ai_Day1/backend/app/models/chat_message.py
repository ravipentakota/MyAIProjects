"""Chat message ORM model."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatMessage(Base):
    """Message sent by user or assistant in a thread."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    thread = relationship("ChatThread", back_populates="messages")
