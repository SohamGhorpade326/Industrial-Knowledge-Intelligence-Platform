import os
import re
import uuid
from datetime import datetime, timezone
from backend.app.core.constants import ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s\-.]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    if not name:
        name = "document"
    unique_id = uuid.uuid4().hex[:8]
    return f"{name}_{unique_id}{ext.lower()}"


def validate_file_extension(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    return ext


def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[dict]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)

        if chunk_text_str.strip():
            chunks.append({
                "text": chunk_text_str,
                "word_start": start,
                "word_end": min(end, len(words)),
                "chunk_index": len(chunks),
            })

        start += chunk_size - overlap

    return chunks


def extract_metadata_from_text(text: str) -> dict:
    metadata = {
        "machines_mentioned": [],
        "keywords": [],
        "has_safety_content": False,
        "has_maintenance_content": False,
        "has_sop_content": False,
    }

    text_lower = text.lower()

    machine_patterns = [
        r"cnc\s*machine", r"hydraulic\s*press", r"conveyor\s*belt",
        r"industrial\s*robot", r"boiler", r"compressor",
        r"lathe", r"drill\s*press", r"milling\s*machine",
    ]
    for pattern in machine_patterns:
        if re.search(pattern, text_lower):
            match_name = re.search(pattern, text_lower).group().title()
            if match_name not in metadata["machines_mentioned"]:
                metadata["machines_mentioned"].append(match_name)

    safety_keywords = ["safety", "hazard", "ppe", "emergency", "caution", "warning", "danger"]
    maintenance_keywords = ["maintenance", "repair", "inspection", "calibration", "lubrication"]
    sop_keywords = ["procedure", "step-by-step", "standard operating", "sop", "protocol"]

    metadata["has_safety_content"] = any(kw in text_lower for kw in safety_keywords)
    metadata["has_maintenance_content"] = any(kw in text_lower for kw in maintenance_keywords)
    metadata["has_sop_content"] = any(kw in text_lower for kw in sop_keywords)

    all_keywords = safety_keywords + maintenance_keywords + sop_keywords
    metadata["keywords"] = [kw for kw in all_keywords if kw in text_lower]

    return metadata


def generate_session_id() -> str:
    return f"session_{uuid.uuid4().hex[:12]}"


def get_current_timestamp() -> datetime:
    return datetime.now(timezone.utc)
