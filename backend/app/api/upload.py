from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.core.config import get_settings
from backend.app.models.models import User
from backend.app.services.document_service import document_service
from backend.app.schemas.schemas import ErrorResponse
from backend.app.core.logging_config import logger

settings = get_settings()
router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("general"),
    machine_name: str = Form(""),
    department: str = Form(""),
    tags: str = Form(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided",
        )

    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    result = await document_service.process_upload(
        db=db,
        file_content=content,
        original_filename=file.filename,
        user_id=current_user.id,
        category=category,
        machine_name=machine_name,
        department=department,
        tags=tag_list,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Upload failed"),
        )

    logger.info(f"Document uploaded by {current_user.email}: {file.filename}")
    return result
