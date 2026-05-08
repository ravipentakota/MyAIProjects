"""Attachment upload and retrieval routes."""
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.attachment import AttachmentDeleteResponse, AttachmentResponse
from app.services.attachment_upload_service import attachment_upload_service

router = APIRouter(tags=["attachments"])


@router.post("/threads/{thread_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    thread_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> AttachmentResponse:
    """Upload an attachment for a thread."""
    return await attachment_upload_service.upload_attachment(db=db, thread_id=thread_id, upload=file)


@router.get("/threads/{thread_id}/attachments", response_model=list[AttachmentResponse])
async def list_thread_attachments(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AttachmentResponse]:
    """List attachment history for a thread."""
    return await attachment_upload_service.list_thread_attachments(db=db, thread_id=thread_id)


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse)
async def get_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
) -> AttachmentResponse:
    """Return attachment metadata."""
    attachment = await attachment_upload_service.get_attachment(db=db, attachment_id=attachment_id)
    return attachment_upload_service.to_attachment_response(attachment)


@router.get("/attachments/{attachment_id}/content")
async def get_attachment_content(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Stream attachment content."""
    return await attachment_upload_service.get_attachment_content(db=db, attachment_id=attachment_id)


@router.delete("/attachments/{attachment_id}", response_model=AttachmentDeleteResponse)
async def delete_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
) -> AttachmentDeleteResponse:
    """Delete an attachment."""
    return await attachment_upload_service.delete_attachment(db=db, attachment_id=attachment_id)
