"""User ORM model."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Application user persisted from OAuth login."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
