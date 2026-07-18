import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.models.models import Document
from backend.app.services.parser_service import parser_service
from backend.app.services.ocr_service import ocr_service
from backend.app.services.embedding_service import embedding_service
from backend.app.services.graph_service import graph_service
from backend.app.utils.helpers import (
    sanitize_filename, validate_file_extension, get_file_type,
    chunk_text, extract_metadata_from_text,
)
from backend.app.core.config import get_settings
from backend.app.core.logging_config import logger

settings = get_settings()


class DocumentService:
    async def process_upload(
        self,
        db: AsyncSession,
        file_content: bytes,
        original_filename: str,
        user_id: Optional[int] = None,
        category: str = "general",
        machine_name: str = "",
        department: str = "",
        tags: list = None,
    ) -> dict:
        if not validate_file_extension(original_filename):
            return {"success": False, "message": "Unsupported file type", "error_code": "INVALID_FILE"}

        safe_filename = sanitize_filename(original_filename)
        file_type = get_file_type(original_filename)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        doc = Document(
            filename=safe_filename,
            original_filename=original_filename,
            title=os.path.splitext(original_filename)[0],
            file_type=file_type,
            file_size=len(file_content),
            category=category,
            tags=tags or [],
            machine_name=machine_name,
            department=department,
            uploaded_by=user_id,
            processing_status="processing",
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)

        try:
            text_result = parser_service.extract_text(file_path, file_type)
            text = text_result.get("text", "")
            page_count = text_result.get("page_count", 0)
            needs_ocr = text_result.get("needs_ocr", False)

            ocr_confidence = 0.0
            if (not text or needs_ocr) and file_type in ("pdf", "png", "jpg", "jpeg"):
                logger.info(f"Running OCR on {safe_filename}")
                if file_type == "pdf":
                    ocr_result = ocr_service.ocr_pdf_pages(file_path)
                else:
                    ocr_result = ocr_service.ocr_image(file_path)

                if ocr_result.get("text"):
                    text = ocr_result["text"]
                    ocr_confidence = ocr_result.get("confidence", 0.0)
                    page_count = ocr_result.get("page_count", page_count)

            doc.text_content = text
            doc.page_count = page_count
            doc.ocr_confidence = ocr_confidence

            metadata = extract_metadata_from_text(text)

            if not machine_name and metadata.get("machines_mentioned"):
                doc.machine_name = metadata["machines_mentioned"][0]

            if text:
                chunks = chunk_text(text)
                chunk_count = embedding_service.store_chunks(
                    document_id=doc.id,
                    chunks=chunks,
                    filename=safe_filename,
                    category=category,
                    machine_name=doc.machine_name,
                )
                doc.chunk_count = chunk_count

            graph_service.update_graph_from_document(
                doc_data={
                    "id": doc.id,
                    "filename": safe_filename,
                    "title": doc.title,
                    "category": category,
                    "file_type": file_type,
                    "machine_name": doc.machine_name,
                },
                metadata=metadata,
            )

            doc.processing_status = "completed"
            await db.flush()

            logger.info(f"Document processed successfully: {safe_filename} ({doc.chunk_count} chunks)")

            return {
                "success": True,
                "document_id": doc.id,
                "filename": safe_filename,
                "chunks_created": doc.chunk_count,
                "pages": page_count,
                "ocr_used": needs_ocr or (not text_result.get("has_selectable_text", True)),
                "ocr_confidence": ocr_confidence,
            }

        except Exception as e:
            logger.error(f"Document processing failed for {safe_filename}: {e}")
            doc.processing_status = "failed"
            await db.flush()
            return {"success": False, "message": str(e), "error_code": "PROCESSING_ERROR"}

    async def get_documents(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        machine_name: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        query = select(Document).order_by(Document.upload_date.desc())

        if category:
            query = query.where(Document.category == category)
        if machine_name:
            query = query.where(Document.machine_name.ilike(f"%{machine_name}%"))
        if search:
            query = query.where(
                Document.original_filename.ilike(f"%{search}%") |
                Document.title.ilike(f"%{search}%") |
                Document.text_content.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        documents = result.scalars().all()

        return {"total": total, "documents": documents}

    async def get_document_by_id(self, db: AsyncSession, doc_id: int) -> Optional[Document]:
        result = await db.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def delete_document(self, db: AsyncSession, doc_id: int) -> bool:
        doc = await self.get_document_by_id(db, doc_id)
        if not doc:
            return False

        embedding_service.delete_document_chunks(doc_id)

        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        await db.delete(doc)
        return True


document_service = DocumentService()
