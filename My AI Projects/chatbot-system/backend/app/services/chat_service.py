from app.ai.gemini_client import GeminiClientPlaceholder


class ChatService:
    """Service layer placeholder for chatbot interactions."""

    def __init__(self) -> None:
        self.gemini_client = GeminiClientPlaceholder()

    async def send_message(self, user_message: str) -> str:
        """Return a placeholder response until chatbot logic is implemented."""
        _ = user_message
        return "Chat service scaffolded. LLM logic not implemented yet."
