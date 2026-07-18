import os
import numpy as np
from typing import Optional
from backend.app.core.logging_config import logger

_ocr_engine = None
_ocr_available = False


def _init_ocr():
    global _ocr_engine, _ocr_available
    try:
        from paddleocr import PaddleOCR
        _ocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            show_log=False,
            use_gpu=False,
        )
        _ocr_available = True
        logger.info("PaddleOCR initialized successfully")
    except Exception as e:
        _ocr_available = False
        logger.warning(f"PaddleOCR not available: {e}. OCR features will be disabled.")


class OCRService:
    def __init__(self):
        if _ocr_engine is None:
            _init_ocr()

    @property
    def is_available(self) -> bool:
        return _ocr_available

    def ocr_image(self, image_path: str) -> dict:
        if not _ocr_available:
            return {
                "text": "",
                "confidence": 0.0,
                "boxes": [],
                "error": "PaddleOCR is not available",
            }

        try:
            result = _ocr_engine.ocr(image_path, cls=True)
            lines = []
            confidences = []
            boxes = []

            if result and result[0]:
                for line in result[0]:
                    bbox = line[0]
                    text = line[1][0]
                    confidence = float(line[1][1])

                    lines.append(text)
                    confidences.append(confidence)
                    boxes.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox,
                    })

            avg_confidence = float(np.mean(confidences)) if confidences else 0.0
            full_text = "\n".join(lines)

            return {
                "text": full_text,
                "confidence": avg_confidence,
                "boxes": boxes,
                "line_count": len(lines),
            }
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return {"text": "", "confidence": 0.0, "boxes": [], "error": str(e)}

    def ocr_pdf_pages(self, pdf_path: str) -> dict:
        if not _ocr_available:
            return {
                "text": "",
                "confidence": 0.0,
                "pages": [],
                "error": "PaddleOCR is not available",
            }

        try:
            import fitz
            doc = fitz.open(pdf_path)
            all_text = ""
            all_confidences = []
            pages = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=200)
                img_path = f"{pdf_path}_page_{page_num}.png"
                pix.save(img_path)

                page_result = self.ocr_image(img_path)
                pages.append({
                    "page_number": page_num + 1,
                    "text": page_result["text"],
                    "confidence": page_result["confidence"],
                })
                all_text += f"\n--- Page {page_num + 1} ---\n{page_result['text']}"
                if page_result["confidence"] > 0:
                    all_confidences.append(page_result["confidence"])

                if os.path.exists(img_path):
                    os.remove(img_path)

            doc.close()

            avg_confidence = float(np.mean(all_confidences)) if all_confidences else 0.0

            return {
                "text": all_text.strip(),
                "confidence": avg_confidence,
                "pages": pages,
                "page_count": len(pages),
            }
        except Exception as e:
            logger.error(f"PDF OCR failed for {pdf_path}: {e}")
            return {"text": "", "confidence": 0.0, "pages": [], "error": str(e)}


ocr_service = OCRService()
