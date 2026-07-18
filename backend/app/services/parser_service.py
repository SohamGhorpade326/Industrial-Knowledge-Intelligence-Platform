import os
import fitz
from typing import Optional
from backend.app.core.logging_config import logger


class ParserService:
    def extract_text_from_pdf(self, file_path: str) -> dict:
        try:
            doc = fitz.open(file_path)
            pages = []
            full_text = ""
            has_selectable_text = False

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").strip()
                if text:
                    has_selectable_text = True
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "has_text": bool(text),
                })
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"

            doc.close()

            return {
                "text": full_text.strip(),
                "pages": pages,
                "page_count": len(pages),
                "has_selectable_text": has_selectable_text,
                "needs_ocr": not has_selectable_text,
            }
        except Exception as e:
            logger.error(f"PDF extraction failed for {file_path}: {e}")
            return {
                "text": "",
                "pages": [],
                "page_count": 0,
                "has_selectable_text": False,
                "needs_ocr": True,
            }

    def extract_text_from_docx(self, file_path: str) -> dict:
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            paragraphs = []
            full_text = ""

            for i, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
                    full_text += text + "\n"

            return {
                "text": full_text.strip(),
                "paragraphs": paragraphs,
                "paragraph_count": len(paragraphs),
            }
        except Exception as e:
            logger.error(f"DOCX extraction failed for {file_path}: {e}")
            return {"text": "", "paragraphs": [], "paragraph_count": 0}

    def extract_text_from_txt(self, file_path: str) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return {"text": text.strip(), "char_count": len(text)}
        except Exception as e:
            logger.error(f"TXT extraction failed for {file_path}: {e}")
            return {"text": "", "char_count": 0}

    def extract_text(self, file_path: str, file_type: str) -> dict:
        file_type = file_type.lower().lstrip(".")

        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return self.extract_text_from_docx(file_path)
        elif file_type == "txt":
            return self.extract_text_from_txt(file_path)
        elif file_type in ("png", "jpg", "jpeg"):
            return {"text": "", "needs_ocr": True}
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return {"text": ""}


parser_service = ParserService()
