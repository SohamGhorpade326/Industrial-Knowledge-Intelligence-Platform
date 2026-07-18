from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.models import User
from backend.app.services.document_service import document_service
from backend.app.schemas.schemas import DocumentResponse, DocumentListResponse

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    category: Optional[str] = Query(None),
    machine_name: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await document_service.get_documents(
        db, category=category, machine_name=machine_name, search=search,
        limit=limit, offset=offset,
    )
    return DocumentListResponse(
        total=result["total"],
        documents=[DocumentResponse.model_validate(d) for d in result["documents"]],
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = await document_service.get_document_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await document_service.delete_document(db, doc_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"success": True, "message": "Document deleted successfully"}
