from app.core.config import get_settings


class GeminiClientPlaceholder:
    """Placeholder for future LangChain + Gemini integration."""

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key

    def get_client(self) -> None:
        """Return a LangChain Gemini client once integration is implemented."""
        # TODO: Initialize and return LangChain Gemini client here.
        # Example target: ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=self.api_key)
        return None
