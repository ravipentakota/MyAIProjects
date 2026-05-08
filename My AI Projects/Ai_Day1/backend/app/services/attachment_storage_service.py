"""Configurable attachment storage layer."""
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class LocalAttachmentStorage:
    """Local filesystem storage implementation for chat attachments."""

    def __init__(self, upload_dir: str) -> None:
        self.base_path = Path(upload_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, stored_name: str) -> Path:
        return self.base_path / stored_name

    async def save(self, upload: UploadFile) -> tuple[str, int]:
        suffix = Path(upload.filename or "upload").suffix
        stored_name = f"{uuid4()}{suffix}"
        target = self.resolve_path(stored_name)

        size_bytes = 0
        with target.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                output.write(chunk)
                size_bytes += len(chunk)

        await upload.seek(0)
        return stored_name, size_bytes

    def delete(self, stored_name: str) -> None:
        target = self.resolve_path(stored_name)
        if target.exists():
            target.unlink()
