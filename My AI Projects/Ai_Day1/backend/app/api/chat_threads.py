"""Chat thread CRUD routes with persistent database storage."""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat_thread import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatThreadCreate,
    ChatThreadResponse,
    ChatThreadUpdate,
)
from app.services.chat_thread_service import chat_thread_service

router = APIRouter(prefix="/threads", tags=["chat-threads"])


@router.get("", response_model=list[ChatThreadResponse])
async def list_threads(
    x_user_id: str = Header(default="local-user"),
    db: AsyncSession = Depends(get_db),
) -> list[ChatThreadResponse]:
    """Return list of user-specific threads."""
    return await chat_thread_service.list_threads(db=db, user_id=x_user_id)


@router.post("", response_model=ChatThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    payload: ChatThreadCreate,
    x_user_id: str = Header(default="local-user"),
    db: AsyncSession = Depends(get_db),
) -> ChatThreadResponse:
    """Create thread endpoint."""
    return await chat_thread_service.create_thread(db=db, user_id=x_user_id, payload=payload)


@router.patch("/{thread_id}", response_model=ChatThreadResponse)
async def update_thread(
    thread_id: str,
    payload: ChatThreadUpdate,
    db: AsyncSession = Depends(get_db),
) -> ChatThreadResponse:
    """Update thread endpoint."""
    try:
        return await chat_thread_service.update_thread(db=db, thread_id=thread_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: str, db: AsyncSession = Depends(get_db)) -> None:
    """Delete thread endpoint."""
    await chat_thread_service.delete_thread(db=db, thread_id=thread_id)


@router.get("/{thread_id}/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Return all messages for a thread."""
    return await chat_thread_service.list_messages(db=db, thread_id=thread_id)


@router.post("/{thread_id}/messages", response_model=list[ChatMessageResponse])
async def send_message(
    thread_id: str,
    payload: ChatMessageCreate,
    x_user_email: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[ChatMessageResponse]:
    """Append user message and generate assistant response."""
    user_identifier = x_user_email or "anonymous@local"
    try:
        return await chat_thread_service.send_message(
            db=db,
            thread_id=thread_id,
            payload=payload,
            user_identifier=user_identifier,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
