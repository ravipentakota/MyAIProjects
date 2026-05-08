"""FastAPI scaffold entry point for auth and chat thread APIs."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.api.attachments import router as attachments_router
from app.api.auth import router as auth_router
from app.api.chat_threads import router as chat_threads_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import ChatAttachment, ChatMessage, ChatThread, User

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Amzur AI Chat API",
    version="0.1.0",
    description="Scaffold API for Supabase auth and chat thread management.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(chat_threads_router, prefix="/api")
app.include_router(attachments_router, prefix="/api")


@app.on_event("startup")
async def startup_event() -> None:
    """Ensure required tables exist for local development."""
    _ = (User, ChatThread, ChatMessage, ChatAttachment)
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except ProgrammingError as exc:
            if "chat_attachments" not in str(exc):
                raise
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)"))


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health endpoint for development checks."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )
