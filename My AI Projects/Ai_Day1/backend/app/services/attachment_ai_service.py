"""Placeholder hooks for future AI-based attachment processing."""
from app.schemas.attachment import AttachmentResponse


class AttachmentAIService:
    """Future extension point for OCR, captioning, extraction, and analysis."""

    async def schedule_processing(self, attachment: AttachmentResponse) -> None:
        """Placeholder async hook for future AI workflows."""
        _ = attachment
        return None


attachment_ai_service = AttachmentAIService()
