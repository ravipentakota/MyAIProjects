"""Conversation memory utilities scoped per chat thread."""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.schemas.chat_thread import ChatMessageResponse, ConversationTurn


class ConversationMemoryService:
    """Manage memory windows for conversation context."""

    def __init__(self, max_conversations: int = 5) -> None:
        self.max_conversations = max_conversations
        self.max_messages = max_conversations * 2

    @staticmethod
    def _to_message_response(message: ChatMessage) -> ChatMessageResponse:
        return ChatMessageResponse(
            id=message.id,
            thread_id=message.thread_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at.isoformat(),
        )

    def _sanitize_payload_history(self, history: list[ConversationTurn] | None) -> list[ChatMessageResponse]:
        if not history:
            return []

        sanitized: list[ChatMessageResponse] = []
        for item in history[-self.max_messages :]:
            role = item.role.strip().lower()
            if role not in {"user", "assistant"}:
                continue

            sanitized.append(
                ChatMessageResponse(
                    id="payload",
                    thread_id="payload",
                    role=role,
                    content=item.content,
                    created_at="",
                )
            )
        return sanitized

    async def get_recent_thread_messages(self, db: AsyncSession, thread_id: str) -> list[ChatMessageResponse]:
        """Load the most recent messages for LLM context, ordered oldest to newest."""
        rows = await db.scalars(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(self.max_messages)
        )
        items = rows.all()
        items.reverse()
        return [self._to_message_response(item) for item in items]

    def resolve_context(
        self,
        persisted_history: list[ChatMessageResponse],
        payload_history: list[ConversationTurn] | None,
    ) -> list[ChatMessageResponse]:
        """Prefer persisted history, fallback to payload history for resilience."""
        if persisted_history:
            return persisted_history[-self.max_messages :]
        return self._sanitize_payload_history(payload_history)

    async def prune_thread_messages(self, db: AsyncSession, thread_id: str) -> None:
        """Delete older messages and keep only the latest memory window."""
        ids = await db.scalars(
            select(ChatMessage.id)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.desc())
        )
        ordered_ids = ids.all()
        if len(ordered_ids) <= self.max_messages:
            return

        ids_to_delete = ordered_ids[self.max_messages :]
        await db.execute(delete(ChatMessage).where(ChatMessage.id.in_(ids_to_delete)))


conversation_memory_service = ConversationMemoryService(max_conversations=5)
