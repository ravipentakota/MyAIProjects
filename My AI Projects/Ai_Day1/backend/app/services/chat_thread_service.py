"""Chat thread service with persistent database storage."""
import json
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chat_message import ChatMessage
from app.models.chat_thread import ChatThread
from app.models.user import User
from app.schemas.chat_thread import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatThreadCreate,
    ChatThreadResponse,
    ChatThreadUpdate,
)
from app.services.attachment_upload_service import attachment_upload_service
from app.services.conversation_memory_service import conversation_memory_service
from app.services.thread_naming_service import thread_naming_service


def _to_thread_response(thread: ChatThread) -> ChatThreadResponse:
    return ChatThreadResponse(
        id=thread.id,
        user_id=thread.user_id,
        title=thread.title,
        created_at=thread.created_at.isoformat(),
    )


def _to_message_response(message: ChatMessage) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=message.id,
        thread_id=message.thread_id,
        role=message.role,
        content=message.content,
        created_at=message.created_at.isoformat(),
        attachments=[],
    )


def _generate_litellm_reply(
    user_input: str,
    history: list[ChatMessageResponse],
    user_identifier: str,
) -> str:
    """Generate assistant reply through Amzur LiteLLM proxy."""
    proxy_url = settings.LITELLM_PROXY_URL.strip()
    api_key = settings.LITELLM_API_KEY.strip()
    model = settings.LLM_MODEL.strip()

    if not proxy_url or not api_key or not model:
        return "LiteLLM configuration is incomplete. Please set proxy URL, API key, and model."

    messages_payload: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant for Amzur users. Keep answers concise and clear.",
        }
    ]

    for message in history:
        messages_payload.append(
            {
                "role": message.role,
                "content": message.content,
            }
        )

    messages_payload.append({"role": "user", "content": user_input})

    body = {
        "model": model,
        "messages": messages_payload,
        "user": user_identifier,
        "metadata": {
            "application": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "user_email": user_identifier,
        },
    }

    endpoint = f"{proxy_url.rstrip('/')}/chat/completions"
    request = Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        ) or "I could not generate a response."
    except Exception:
        return "I could not generate a response right now. Please try again in a moment."


class ChatThreadService:
    """Service for chat thread management backed by database tables."""

    async def _with_attachments(
        self,
        db: AsyncSession,
        messages: list[ChatMessageResponse],
    ) -> list[ChatMessageResponse]:
        for message in messages:
            message.attachments = await attachment_upload_service.list_message_attachments(db=db, message_id=message.id)
        return messages

    async def _ensure_user_exists(self, db: AsyncSession, user_id: str) -> None:
        """Create a lightweight local user when chat APIs are used without OAuth."""
        existing = await db.scalar(select(User).where(User.id == user_id))
        if existing:
            return

        fallback_email = f"{user_id}@local.user"
        taken = await db.scalar(select(User).where(User.email == fallback_email))
        if taken:
            fallback_email = f"{user_id}-{taken.id}@local.user"

        db.add(User(id=user_id, email=fallback_email, full_name=None, google_id=None))
        await db.commit()

    async def list_threads(self, db: AsyncSession, user_id: str) -> list[ChatThreadResponse]:
        """Load user-specific chat threads."""
        rows = await db.scalars(
            select(ChatThread).where(ChatThread.user_id == user_id).order_by(ChatThread.created_at.desc())
        )
        return [_to_thread_response(item) for item in rows.all()]

    async def create_thread(
        self,
        db: AsyncSession,
        user_id: str,
        payload: ChatThreadCreate,
    ) -> ChatThreadResponse:
        """Create chat thread."""
        await self._ensure_user_exists(db=db, user_id=user_id)
        title = payload.title or thread_naming_service.generate_thread_name("")
        thread = ChatThread(user_id=user_id, title=title)
        db.add(thread)
        await db.commit()
        await db.refresh(thread)
        return _to_thread_response(thread)

    async def update_thread(
        self,
        db: AsyncSession,
        thread_id: str,
        payload: ChatThreadUpdate,
    ) -> ChatThreadResponse:
        """Update chat thread title."""
        thread = await db.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if not thread:
            raise ValueError("Thread not found")

        thread.title = payload.title or thread.title
        await db.commit()
        await db.refresh(thread)
        return _to_thread_response(thread)

    async def delete_thread(self, db: AsyncSession, thread_id: str) -> None:
        """Delete chat thread and related messages."""
        thread = await db.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if thread:
            await db.delete(thread)
            await db.commit()

    async def list_messages(self, db: AsyncSession, thread_id: str) -> list[ChatMessageResponse]:
        """List messages in a thread."""
        rows = await db.scalars(
            select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at.asc())
        )
        messages = [_to_message_response(item) for item in rows.all()]
        return await self._with_attachments(db=db, messages=messages)

    async def send_message(
        self,
        db: AsyncSession,
        thread_id: str,
        payload: ChatMessageCreate,
        user_identifier: str,
    ) -> list[ChatMessageResponse]:
        """Append user message and generated assistant response."""
        thread = await db.scalar(select(ChatThread).where(ChatThread.id == thread_id))
        if not thread:
            raise ValueError("Thread not found")

        persisted_memory = await conversation_memory_service.get_recent_thread_messages(
            db=db,
            thread_id=thread_id,
        )
        history = conversation_memory_service.resolve_context(
            persisted_history=persisted_memory,
            payload_history=payload.history,
        )

        user_message = ChatMessage(thread_id=thread_id, role="user", content=payload.content)
        db.add(user_message)
        await db.flush()
        await attachment_upload_service.attach_to_message(
            db=db,
            thread_id=thread_id,
            message_id=user_message.id,
            attachment_ids=payload.attachment_ids or [],
        )

        assistant_content = _generate_litellm_reply(
            user_input=payload.content,
            history=history,
            user_identifier=user_identifier,
        )

        assistant_message = ChatMessage(thread_id=thread_id, role="assistant", content=assistant_content)
        db.add(assistant_message)

        if thread.title == "New Chat":
            thread.title = thread_naming_service.generate_thread_name(payload.content)

        await db.commit()

        await conversation_memory_service.prune_thread_messages(db=db, thread_id=thread_id)
        await db.commit()

        rows = await db.scalars(
            select(ChatMessage).where(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at.asc())
        )
        messages = [_to_message_response(item) for item in rows.all()]
        return await self._with_attachments(db=db, messages=messages)


chat_thread_service = ChatThreadService()
