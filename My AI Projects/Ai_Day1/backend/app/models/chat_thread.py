"""Chat thread ORM model."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatThread(Base):
    """Thread created by a user."""

    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Chat")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")
